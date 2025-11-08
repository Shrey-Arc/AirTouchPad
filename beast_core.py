import time
import json
import os
import collections
import traceback
from datetime import datetime
from utils.config import Config
from handtracker import HandTracker
from gesturelogic import GestureEngine
from eventmapper import EventMapper

# File paths
BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(BASE_DIR, 'airtouch.log')
STATUS_FILE = os.path.join(BASE_DIR, 'status.json')
DEBUG_DUMP_FILE = os.path.join(BASE_DIR, 'debug_dump.json')

# Rotating log settings
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_FILES = 3

# Debug snapshot buffer (circular)
DEBUG_SNAPSHOTS = collections.deque(maxlen=200)

def setup_logging():
    """Initialize logging with rotation"""
    # Check if log file needs rotation
    if os.path.exists(LOG_FILE):
        size = os.path.getsize(LOG_FILE)
        if size > MAX_LOG_SIZE:
            rotate_logs()

def rotate_logs():
    """Rotate log files"""
    try:
        # Shift existing logs
        for i in range(MAX_LOG_FILES - 1, 0, -1):
            old_file = f"{LOG_FILE}.{i}"
            new_file = f"{LOG_FILE}.{i + 1}"
            if os.path.exists(old_file):
                if i == MAX_LOG_FILES - 1 and os.path.exists(new_file):
                    os.remove(new_file)
                os.rename(old_file, new_file)
        
        # Move current log to .1
        if os.path.exists(LOG_FILE):
            os.rename(LOG_FILE, f"{LOG_FILE}.1")
    except Exception as e:
        print(f"[LOG] Failed to rotate logs: {e}")

def log(message, level='INFO'):
    """Write timestamped log entry"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)
    except Exception as e:
        print(f"[LOG ERROR] {e}")
    
    # Also print to console
    print(log_line.strip())

def write_status(data):
    """Write current status to JSON file"""
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def capture_debug_snapshot(hands, gestures, frame_info=None):
    """Capture snapshot for debugging"""
    snapshot = {
        'timestamp': time.time(),
        'datetime': datetime.now().isoformat(),
        'hands': hands,
        'gestures': gestures,
        'frame_info': frame_info or {}
    }
    DEBUG_SNAPSHOTS.append(snapshot)

def save_debug_dump():
    """Save debug snapshots to file"""
    try:
        data = {
            'dump_time': datetime.now().isoformat(),
            'snapshot_count': len(DEBUG_SNAPSHOTS),
            'snapshots': list(DEBUG_SNAPSHOTS)
        }
        
        with open(DEBUG_DUMP_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        log(f"Debug dump saved: {len(DEBUG_SNAPSHOTS)} snapshots", 'DEBUG')
        print(f"\n✓ Debug dump saved to: {DEBUG_DUMP_FILE}")
        return True
    except Exception as e:
        log(f"Failed to save debug dump: {e}", 'ERROR')
        return False

def print_startup_banner():
    """Print startup information"""
    print("\n" + "="*60)
    print("   ✋ AirTouchPad - Hand Gesture Control System")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log File: {LOG_FILE}")
    print(f"Status File: {STATUS_FILE}")
    print(f"Debug Dump: {DEBUG_DUMP_FILE}")
    print("\nPress Ctrl+C to stop gracefully")
    print("="*60 + "\n")

def main():
    # Setup
    setup_logging()
    print_startup_banner()
    
    log("="*50, 'INFO')
    log("AirTouchPad Starting", 'INFO')
    log("="*50, 'INFO')
    
    # Check for command-line arguments (camera index, model complexity)
    import sys
    camera_index = 0
    model_complexity = 0
    
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            log(f"Using camera index: {camera_index}", 'INFO')
        except ValueError:
            log(f"Invalid camera index: {sys.argv[1]}, using default (0)", 'WARN')
    
    if len(sys.argv) > 2:
        try:
            model_complexity = int(sys.argv[2])
            log(f"Using model complexity: {model_complexity}", 'INFO')
        except ValueError:
            log(f"Invalid model complexity: {sys.argv[2]}, using default (0)", 'WARN')
    
    # Initialize components
    try:
        log("Initializing configuration...", 'INFO')
        cfg = Config()
        
        log(f"Initializing hand tracker (camera: {camera_index}, model: {model_complexity})...", 'INFO')
        tracker = HandTracker(cfg, camera_index, model_complexity)
        
        log("Initializing gesture engine...", 'INFO')
        engine = GestureEngine(cfg)
        
        log("Initializing event mapper...", 'INFO')
        mapper = EventMapper(cfg)
        
        log("Initialization complete - Starting main loop", 'INFO')
        
    except Exception as e:
        log(f"FATAL: Initialization failed: {e}", 'ERROR')
        log(traceback.format_exc(), 'ERROR')
        return 1
    
    # Check permissions
    try:
        from os_handlers import get_permission_instructions
        instructions = get_permission_instructions()
        if instructions and "Required" in instructions:
            log("WARNING: Permission issues detected", 'WARN')
            log(instructions, 'WARN')
            print("\n⚠️  PERMISSION WARNING:")
            print(instructions)
            print("\nContinuing anyway... Some features may not work.\n")
    except Exception:
        pass
    
    # Main loop
    frame_count = 0
    gesture_count = 0
    error_count = 0
    start_time = time.time()
    last_status_update = 0
    
    try:
        while True:
            loop_start = time.time()
            
            try:
                # Get hand tracking data
                hands, frame = tracker.step()
                frame_count += 1
                
                # Process gestures
                gestures = engine.update(hands)
                
                # Capture debug snapshot every 10th frame or when gesture detected
                if gestures or frame_count % 10 == 0:
                    frame_info = {
                        'frame_count': frame_count,
                        'hand_count': len(hands) if hands else 0
                    }
                    capture_debug_snapshot(hands, gestures, frame_info)
                
                # Handle gestures
                if gestures:
                    for g in gestures:
                        gesture_count += 1
                        mapper.handle(g)
                        log(f"Gesture #{gesture_count}: {g.get('type')} (conf: {g.get('confidence', 1.0):.2f})", 'GESTURE')
                
                # Update status file periodically (every 5 seconds)
                if time.time() - last_status_update > 5:
                    runtime = time.time() - start_time
                    status = {
                        'timestamp': time.time(),
                        'datetime': datetime.now().isoformat(),
                        'runtime_seconds': runtime,
                        'frame_count': frame_count,
                        'gesture_count': gesture_count,
                        'error_count': error_count,
                        'fps': frame_count / runtime if runtime > 0 else 0,
                        'recent_gestures': gestures,
                        'hand_count': len(hands) if hands else 0
                    }
                    write_status(status)
                    last_status_update = time.time()
                
            except Exception as e:
                error_count += 1
                log(f"Error in main loop (error #{error_count}): {e}", 'ERROR')
                if error_count > 100:
                    log("Too many errors (>100), stopping", 'FATAL')
                    break
            
            # Frame timing
            loop_time = time.time() - loop_start
            sleep_time = max(0, 0.01 - loop_time)  # Target ~100 FPS max
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        log("Received interrupt signal (Ctrl+C)", 'INFO')
        print("\n\n👋 Stopping AirTouchPad gracefully...")
        
    except Exception as e:
        log(f"FATAL: Unexpected error in main loop: {e}", 'ERROR')
        log(traceback.format_exc(), 'ERROR')
        print("\n\n❌ Fatal error occurred!")
        
    finally:
        # Cleanup
        log("Shutting down...", 'INFO')
        
        # Print statistics
        runtime = time.time() - start_time
        print("\n" + "="*60)
        print("Session Statistics:")
        print(f"  Runtime: {runtime:.1f} seconds")
        print(f"  Frames Processed: {frame_count}")
        print(f"  Gestures Detected: {gesture_count}")
        print(f"  Errors: {error_count}")
        print(f"  Average FPS: {frame_count/runtime:.1f}" if runtime > 0 else "  Average FPS: N/A")
        print("="*60)
        
        # Save debug dump
        if DEBUG_SNAPSHOTS:
            print("\nSaving debug information...")
            save_debug_dump()
        
        # Shutdown tracker
        try:
            tracker.shutdown()
            log("Hand tracker shutdown complete", 'INFO')
        except Exception as e:
            log(f"Error during tracker shutdown: {e}", 'ERROR')
        
        log("Shutdown complete", 'INFO')
        log("="*50, 'INFO')
        
        print("\n✓ AirTouchPad stopped\n")
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)