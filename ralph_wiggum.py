#!/usr/bin/env python3
import os
import subprocess
import time

PLAN_FILE = "PROJECT_PLAN.md"

def has_remaining_tasks():
    if not os.path.exists(PLAN_FILE):
        return False
    with open(PLAN_FILE) as f:
        content = f.read()
        return "[ ]" in content

def run_driver():
    print("Ralph Wiggum driver starting...")

    while has_remaining_tasks():
        prompt = (
            f"Refer to {PLAN_FILE} and execute the next 'not-done' step (marked with [ ]). "
            "Work through the task thoroughly. Once the step is fully completed and you have verified the result, "
            f"update {PLAN_FILE} to mark the task as done with `[x]` and then output the sigil '<DONE!>' to indicate completion. Then STOP!"
            "You are running in a sandbox, so you have full access to any command. Always use `uv` to run Python script."
        )

        print("\n" + "="*80)
        print(f"Starting Gemini instance at {time.strftime('%H:%M:%S')}...")
        print("="*80 + "\n")

        # Execute gemini with the prompt, sandbox, and yolo mode
        process = subprocess.Popen(
            ["gemini", "--sandbox", "--yolo", "-p", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        done_detected = False
        try:
            for line in process.stdout:
                print(line, end="", flush=True)
                if "<DONE!>" in line:
                    done_detected = True

            process.wait()

            if done_detected:
                print("\n[Driver] Sigil <DONE!> detected. Moving to next task...")
            else:
                print("\n[Driver] Gemini process finished without <DONE!> sigil. Checking for updates...")

            # Short pause before next iteration to avoid rapid spinning on errors
            time.sleep(2)

        except KeyboardInterrupt:
            print("\n[Driver] Interrupted by user. Shutting down...")
            process.terminate()
            break
        except Exception as e:
            print(f"\n[Driver] An unexpected error occurred: {e}")
            break

    if not has_remaining_tasks():
        print("\nAll tasks in PROJECT_PLAN.md are marked as done. Ralph Wiggum is going home!")

if __name__ == "__main__":
    run_driver()
