# scripts/ingest_navs.py
import os
import asyncio
import argparse
import json
import time
from datetime import datetime, timezone, date
from typing import List, Dict, Tuple, Optional
import httpx
from pathlib import Path

from app.database import connect_to_db, disconnect_from_db
from app.models import FundNav
from app.funds import mf

API_BASE = "https://api.mfapi.in/mf"

class CheckpointManager:
    """Manages checkpoint persistence for resumable ingestion"""
    def __init__(self, filename="checkpoints/nav_checkpoint.json"):
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 Checkpoint saved to {self.filename}")
        except Exception as e:
            print(f"❗ Failed to save checkpoint: {e}")

    def load(self) -> dict:
        if not self.filename.exists():
            return {}
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"📂 Checkpoint loaded from {self.filename}")
            return data
        except Exception as e:
            print(f"❗ Failed to load checkpoint: {e}")
            return {}

    def clear(self):
        try:
            if self.filename.exists():
                self.filename.unlink()
                print(f"🗑️ Checkpoint cleared ({self.filename})")
        except Exception as e:
            print(f"❗ Failed to clear checkpoint: {e}")

class ErrorLogger:
    """Persistent logging of ingestion errors for analysis"""
    def __init__(self, filename="logs/ingestion_errors.jsonl"):
        self.filename = Path(filename)
        self.filename.parent.mkdir(parents=True, exist_ok=True)

    def log(self, scheme: str, stage: str, data: any, error: Exception):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "scheme": scheme,
            "stage": stage,
            "data": str(data)[:1000] if data else None,  # Limit data size
            "error": str(error),
            "error_type": type(error).__name__,
        }
        try:
            with open(self.filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            print(f"❗ Failed to log error: {e}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Ingest NAV data with checkpoint support")
    parser.add_argument("--only-latest", action="store_true", 
                       help="Fetch and insert only latest NAV per scheme")
    parser.add_argument("--since", type=str, default=None, 
                       help="Start date YYYY-MM-DD")
    parser.add_argument("--until", type=str, default=None, 
                       help="End date YYYY-MM-DD")
    parser.add_argument("--scheme-codes", type=str, default=None, 
                       help="Comma separated scheme codes")
    parser.add_argument("--funds-file", type=str, default=None, 
                       help="File path with scheme codes (one per line)")
    parser.add_argument("--max-concurrency", type=int, default=8, 
                       help="Max concurrent HTTP requests")
    parser.add_argument("--timeout", type=float, default=20, 
                       help="HTTP request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, 
                       help="HTTP retry attempts")
    parser.add_argument("--sleep", type=float, default=0.5, 
                       help="Base sleep seconds between retries")
    parser.add_argument("--limit", type=int, default=None, 
                       help="Limit number of schemes to process")
    parser.add_argument("--checkpoint-file", type=str, 
                       default="checkpoints/nav_checkpoint.json",
                       help="Checkpoint file path")
    parser.add_argument("--checkpoint-every", type=int, default=50, 
                       help="Save checkpoint after every N schemes")
    parser.add_argument("--resume", action="store_true", 
                       help="Resume from last checkpoint")
    return parser.parse_args()

def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration"""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

async def fetch_nav_history(session: httpx.AsyncClient, scheme: str, 
                          retries: int, sleep: float) -> Tuple[List[dict], Dict]:
    """Fetch NAV history from MFAPI with retry logic"""
    url = f"{API_BASE}/{scheme}"
    last_exception = None
    
    for attempt in range(1, retries + 1):
        try:
            response = await session.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", []), data.get("meta", {})
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"🚫 Scheme {scheme} not found (404). Skipping.")
                return [], {}
            last_exception = e
        except Exception as e:
            last_exception = e
        
        if attempt < retries:
            await asyncio.sleep(sleep * attempt)
    
    # If all retries failed, return empty data to continue with other schemes
    print(f"❌ Failed to fetch {scheme} after {retries} attempts: {last_exception}")
    return [], {}

def clean_and_prepare_navs(raw_navs: List[dict], fund_id: str, meta: Dict, 
                          only_latest: bool, since: Optional[date], 
                          until: Optional[date]) -> List[Tuple]:
    """Clean and prepare NAV data for database insertion"""
    cleaned = []
    seen_dates = set()
    
    if not raw_navs:
        return cleaned
    
    # Choose sequence based on only_latest flag
    navs_sequence = raw_navs[-1:] if only_latest else reversed(raw_navs)

    # Parse AUM safely
    aum_val = None
    if meta.get("aum") not in (None, "", "NA"):
        try:
            aum_val = float(meta.get("aum"))
        except (ValueError, TypeError):
            aum_val = None

    scheme_name = meta.get("scheme_name")
    category = meta.get("scheme_category")

    for idx, item in enumerate(navs_sequence):
        try:
            # Check for required fields
            if not isinstance(item, dict):
                print(f"⚠️ Fund {fund_id}: Invalid item type at index {idx}")
                continue
                
            date_str = item.get("date")
            nav_str = item.get("nav")
            
            if not date_str or not nav_str:
                print(f"⚠️ Fund {fund_id}: Missing date/nav at index {idx}: {item}")
                continue

            # Parse date
            d = datetime.strptime(str(date_str).strip(), "%d-%m-%Y").date()
            
            # Apply date filters
            if since and d < since:
                continue
            if until and d > until:
                continue
            if d in seen_dates:
                continue
            
            # Parse NAV
            nav = float(str(nav_str).strip())
            
            seen_dates.add(d)
            cleaned.append((d, nav, aum_val, scheme_name, category))
            
        except Exception as e:
            print(f"⚠️ Fund {fund_id}: Error parsing record {idx}: {e}")
            error_logger.log(fund_id, "parsing", item, e)
            continue

    return cleaned
import json
import traceback
from datetime import datetime, timezone, date
from pathlib import Path
from typing import List, Tuple

async def upsert_navs(fund_id: str, rows: List[Tuple]) -> int:
    """
    Production-ready NAV upsert function with comprehensive validation and error handling.
    
    Args:
        fund_id: The mutual fund scheme ID
        rows: List of tuples containing (date, nav, aum, scheme_name, category)
    
    Returns:
        int: Count of successfully processed records
    """
    count = 0
    skipped = 0
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    for date_val, nav, aum, scheme_name, category in rows:
        try:
            # === INPUT VALIDATION ===
            # Validate essential fields
            if not isinstance(nav, (int, float)) or nav is None:
                print(f"⚠️  Skipping {fund_id} on {date_val}: Invalid NAV ({nav}, {type(nav).__name__})")
                skipped += 1
                continue
                
            if date_val is None or not isinstance(date_val, date):
                print(f"⚠️  Skipping {fund_id}: Invalid date ({date_val}, {type(date_val).__name__})")
                skipped += 1
                continue

            # === PAYLOAD CONSTRUCTION ===
            # Build base payload with required fields
            payload = {
                "fund_id": str(fund_id),
                "date": date_val,
                "nav": float(nav),
                "source": "api.mfapi.in",
                "updated_at": datetime.now(timezone.utc),
            }
            
            # Conditionally add optional fields only if valid
            if aum is not None and isinstance(aum, (int, float)):
                try:
                    payload["aum"] = float(aum)
                except (ValueError, TypeError):
                    pass  # Skip invalid aum values
            
            if scheme_name and isinstance(scheme_name, str) and scheme_name.strip():
                payload["scheme_name"] = str(scheme_name).strip()[:500]  # Limit length
                
            if category and isinstance(category, str) and category.strip():
                payload["category"] = str(category).strip()[:200]  # Limit length

            # === DATABASE OPERATION ===
            success = False
            operation_type = None
            
            try:
                # Attempt direct insertion first (most common case for new data)
                await FundNav.objects.create(**payload)
                success = True
                operation_type = "created"
                
            except Exception as create_error:
                # Check if it's a duplicate key constraint error
                error_str = str(create_error).lower()
                if "duplicate key" in error_str or "unique constraint" in error_str:
                    try:
                        # Prepare update payload (exclude primary/unique key fields)
                        update_payload = {k: v for k, v in payload.items() 
                                        if k not in ['fund_id', 'date']}
                        
                        # Attempt to update existing record
                        result = await FundNav.objects.filter(
                            fund_id=fund_id, 
                            date=date_val
                        ).update(**update_payload)
                        
                        if result:
                            success = True
                            operation_type = "updated"
                        else:
                            # No existing record found - this shouldn't happen with duplicate key error
                            # Most likely the original insert actually succeeded despite the error
                            # This can happen with race conditions or phantom reads
                            success = True
                            operation_type = "created (retry)"
                            
                    except Exception as update_error:
                        # Both create and update failed
                        print(f"❌ Failed both create and update for {fund_id} on {date_val}")
                        print(f"   Create error: {str(create_error)[:100]}...")
                        print(f"   Update error: {str(update_error)[:100]}...")
                        
                        # Log to error file for analysis
                        await log_error(fund_id, date_val, create_error, {
                            'nav': nav, 'aum': aum, 'scheme_name': scheme_name, 
                            'category': category, 'payload': payload,
                            'secondary_error': str(update_error)
                        })
                        continue
                else:
                    # Different error than duplicate key - re-raise to be caught by outer try-catch
                    raise create_error
            
            # Log success and increment counter
            if success:
                count += 1
                # Only print every 50th success to reduce noise
                if count % 50 == 0 or operation_type == "updated":
                    print(f"✅ {operation_type.capitalize()}: {fund_id} on {date_val} (NAV: {nav}) - Total: {count}")
            
        except Exception as e:
            # === COMPREHENSIVE ERROR LOGGING ===
            print(f"💥 ERROR processing {fund_id} on {date_val}: {e}")
            
            await log_error(fund_id, date_val, e, {
                'nav': nav, 'aum': aum, 'scheme_name': scheme_name, 
                'category': category, 'payload': payload if 'payload' in locals() else None
            })
            
            # Continue processing remaining records
            continue
    
    # Print final summary
    total_processed = count + skipped
    if total_processed > 0:
        success_rate = (count / total_processed) * 100
        print(f"📊 {fund_id} Summary: {count} processed, {skipped} skipped ({success_rate:.1f}% success)")
    
    return count


async def log_error(fund_id: str, date_val, error: Exception, context: dict):
    """Helper function to log detailed error information"""
    try:
        error_details = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'fund_id': fund_id,
            'date': str(date_val),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': {
                'nav': {'value': context.get('nav'), 'type': type(context.get('nav')).__name__},
                'aum': {'value': context.get('aum'), 'type': type(context.get('aum')).__name__},
                'scheme_name': {'value': context.get('scheme_name'), 'type': type(context.get('scheme_name')).__name__},
                'category': {'value': context.get('category'), 'type': type(context.get('category')).__name__},
            },
            'payload': {k: {'value': v, 'type': type(v).__name__} 
                       for k, v in context.get('payload', {}).items()} if context.get('payload') else None,
            'secondary_error': context.get('secondary_error')
        }
        
        with open('logs/detailed_db_errors.jsonl', 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_details, default=str) + '\n')
            
    except Exception as log_error:
        print(f"⚠️  Failed to write error log: {log_error}")


# === BATCH PROCESSING HELPER ===
async def process_scheme_batch(scheme_code: str, nav_data: List[Tuple], 
                             batch_size: int = 1000) -> dict:
    """
    Process NAV data for a single scheme in batches with progress reporting.
    
    Args:
        scheme_code: The mutual fund scheme identifier
        nav_data: List of NAV records as tuples
        batch_size: Number of records to process per batch
    
    Returns:
        dict: Processing statistics
    """
    total_records = len(nav_data)
    total_processed = 0
    
    print(f"🚀 Processing {total_records} NAV records for scheme {scheme_code}")
    
    # Process in batches to manage memory and provide progress updates
    for i in range(0, total_records, batch_size):
        batch_end = min(i + batch_size, total_records)
        batch_data = nav_data[i:batch_end]
        
        batch_processed = await upsert_navs(scheme_code, batch_data)
        total_processed += batch_processed
        
        progress = (batch_end / total_records) * 100
        print(f"📈 Batch {i//batch_size + 1}: {batch_processed}/{len(batch_data)} processed "
              f"({progress:.1f}% complete)")
    
    # Final statistics
    success_rate = (total_processed / total_records * 100) if total_records > 0 else 0
    
    stats = {
        'scheme_code': scheme_code,
        'total_records': total_records,
        'processed': total_processed,
        'success_rate': success_rate
    }
    
    print(f"🎉 Completed {scheme_code}: {total_processed}/{total_records} processed "
          f"({success_rate:.1f}% success rate)")
    
    return stats


# === HELPER FUNCTION FOR BATCH PROCESSING ===
async def process_scheme_navs(scheme_code: str, nav_data: List[Tuple], 
                            batch_size: int = 100) -> dict:
    """
    Process NAV data for a single scheme in batches.
    
    Args:
        scheme_code: The mutual fund scheme identifier
        nav_data: List of NAV records as tuples
        batch_size: Number of records to process per batch
    
    Returns:
        dict: Processing statistics
    """
    total_records = len(nav_data)
    total_processed = 0
    total_errors = 0
    
    print(f"🔄 Processing {total_records} NAV records for scheme {scheme_code}")
    
    # Process in batches to manage memory and provide progress updates
    for i in range(0, total_records, batch_size):
        batch_end = min(i + batch_size, total_records)
        batch_data = nav_data[i:batch_end]
        
        batch_processed = await upsert_navs(scheme_code, batch_data)
        batch_errors = len(batch_data) - batch_processed
        
        total_processed += batch_processed
        total_errors += batch_errors
        
        progress = ((batch_end / total_records) * 100)
        print(f"📊 Batch {i//batch_size + 1}: {batch_processed}/{len(batch_data)} processed "
              f"({progress:.1f}% complete)")
    
    # Final statistics
    success_rate = (total_processed / total_records * 100) if total_records > 0 else 0
    
    stats = {
        'scheme_code': scheme_code,
        'total_records': total_records,
        'processed': total_processed,
        'errors': total_errors,
        'success_rate': success_rate
    }
    
    print(f"✅ Completed {scheme_code}: {total_processed}/{total_records} processed "
          f"({success_rate:.1f}% success rate)")
    
    return stats

async def process_scheme(semaphore: asyncio.Semaphore, session: httpx.AsyncClient,
                        scheme_code: str, retries: int, sleep: float,
                        only_latest: bool, since: Optional[date], 
                        until: Optional[date]) -> Tuple[str, int, Optional[str]]:
    """Process a single scheme: fetch, clean, and store NAV data"""
    async with semaphore:
        try:
            raw_navs, meta = await fetch_nav_history(session, scheme_code, retries, sleep)
            
            rows = clean_and_prepare_navs(raw_navs, scheme_code, meta, 
                                        only_latest, since, until)
            
            written = await upsert_navs(scheme_code, rows)
            return scheme_code, written, None
            
        except Exception as e:
            print(f"❌ Error processing scheme {scheme_code}: {e}")
            error_logger.log(scheme_code, "process_scheme", None, e)
            return scheme_code, 0, str(e)

def load_scheme_codes(args) -> Dict[str, str]:
    """Load scheme codes from various sources"""
    if args.scheme_codes:
        codes = [c.strip() for c in args.scheme_codes.split(",") if c.strip()]
        return {c: c for c in codes}
    
    if args.funds_file and os.path.exists(args.funds_file):
        with open(args.funds_file, "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
        return {c: c for c in codes}
    
    return mf.get_scheme_codes()

async def main():
    """Main ingestion function"""
    args = parse_args()
    
    # Parse date arguments
    since = datetime.strptime(args.since, "%Y-%m-%d").date() if args.since else None
    until = datetime.strptime(args.until, "%Y-%m-%d").date() if args.until else None

    # Initialize managers
    checkpoint_mgr = CheckpointManager(args.checkpoint_file)
    
    # Load checkpoint if resuming
    processed_schemes = set()
    if args.resume:
        checkpoint_data = checkpoint_mgr.load()
        processed_schemes = set(checkpoint_data.get("processed_schemes", []))
        print(f"⏳ Resuming from checkpoint: {len(processed_schemes)} schemes already processed")

    # Connect to database
    await connect_to_db()
    
    try:
        # Load scheme codes
        all_codes = load_scheme_codes(args)
        codes = list(all_codes.keys())
        
        if args.limit:
            codes = codes[:args.limit]

        # Filter out already processed schemes
        codes = [c for c in codes if c not in processed_schemes]
        
        if not codes:
            print("✅ No new schemes to process.")
            return

        print(f"🚀 Starting ingestion of {len(codes)} schemes")

        # Setup HTTP client
        limits = httpx.Limits(
            max_connections=args.max_concurrency, 
            max_keepalive_connections=args.max_concurrency
        )
        timeout = httpx.Timeout(args.timeout)
        semaphore = asyncio.Semaphore(args.max_concurrency)

        # Tracking variables
        total_written = 0
        total_errors = 0
        completed = 0
        start_time = time.perf_counter()

        async with httpx.AsyncClient(limits=limits, timeout=timeout, 
                                   headers={"Accept": "application/json"}) as session:

            # Process in batches for checkpointing
            batch_size = args.checkpoint_every
            total_batches = (len(codes) - 1) // batch_size + 1

            for batch_idx in range(0, len(codes), batch_size):
                batch_codes = codes[batch_idx:batch_idx + batch_size]
                batch_num = batch_idx // batch_size + 1
                
                print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch_codes)} schemes)")

                # Create tasks for this batch
                tasks = {
                    asyncio.create_task(
                        process_scheme(semaphore, session, scheme, args.retries, 
                                     args.sleep, args.only_latest, since, until)
                    ) for scheme in batch_codes
                }

                try:
                    # Process batch
                    for future in asyncio.as_completed(tasks):
                        scheme_code, written, error = await future
                        completed += 1
                        
                        if error:
                            total_errors += 1
                            print(f"[ERROR] {scheme_code}: {error}")
                        else:
                            total_written += written
                            processed_schemes.add(scheme_code)
                            print(f"[OK] {scheme_code}: {written} rows")

                        # Progress tracking
                        elapsed = time.perf_counter() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        remaining = len(codes) - completed
                        eta = remaining / rate if rate > 0 else 0
                        percent = (completed / len(codes)) * 100
                        
                        print(f"Progress: {completed}/{len(codes)} ({percent:.1f}%), "
                              f"ETA ~ {format_duration(eta)}")

                    # Save checkpoint after each batch
                    checkpoint_data = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "processed_schemes": list(processed_schemes),
                        "total_written": total_written,
                        "total_errors": total_errors,
                        "completed": completed,
                        "args": {
                            "since": args.since,
                            "until": args.until,
                            "only_latest": args.only_latest,
                            "limit": args.limit
                        }
                    }
                    checkpoint_mgr.save(checkpoint_data)
                    print(f"🏁 Batch {batch_num} completed. Written: {total_written}, Errors: {total_errors}")

                except (KeyboardInterrupt, asyncio.CancelledError):
                    print("\n🛑 Interrupted! Saving checkpoint...")
                    checkpoint_mgr.save({
                        "timestamp": datetime.utcnow().isoformat(),
                        "processed_schemes": list(processed_schemes),
                        "total_written": total_written,
                        "total_errors": total_errors,
                        "completed": completed,
                        "status": "interrupted"
                    })
                    
                    # Cancel remaining tasks
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                    raise

        # Ingestion completed successfully
        print(f"\n✅ Ingestion completed!")
        print(f"📊 Final stats: {total_written} rows written, {total_errors} errors")
        checkpoint_mgr.clear()

    finally:
        await disconnect_from_db()

# Global error logger instance (initialized at module level)
error_logger = ErrorLogger()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Progress saved in checkpoint.")
        print("💡 Use --resume flag to continue from where you left off.")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
