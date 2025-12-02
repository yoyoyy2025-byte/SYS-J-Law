import os
import signal

print("🕵️‍♂️ Ngrok 프로세스를 찾는 중...")

# 실행 중인 모든 프로세스 뒤지기
try:
    # /proc 폴더 내의 숫자(PID) 폴더들만 리스트업
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    
    found = False
    for pid in pids:
        try:
            # 각 프로세스의 이름(cmdline) 확인
            with open(os.path.join('/proc', pid, 'cmdline'), 'rb') as f:
                cmd = f.read().decode('utf-8')
                
                # 이름에 'ngrok'이 들어있으면 사살
                if 'ngrok' in cmd:
                    print(f"🔫 잡았다! Ngrok (PID: {pid}) -> 강제 종료 시도")
                    os.kill(int(pid), signal.SIGKILL) # 강제 종료 신호 발사
                    found = True
        except Exception:
            # 이미 죽었거나 접근 권한 없는 프로세스는 패스
            continue

    if found:
        print("✅ 모든 Ngrok 프로세스를 정리했습니다.")
    else:
        print("❓ 실행 중인 Ngrok을 찾지 못했습니다. (이미 꺼진 듯합니다)")

except Exception as e:
    print(f"❌ 오류 발생: {e}")