# AIoT 영유아 침대 난간 접근 모니터링

HC-SR04 초음파 센서로 측정한 거리를 Raspberry Pi 5에서 수집하고, nCube를 거쳐 Mobius oneM2M 서버에 저장한 뒤 리소스 브라우저와 Freeboard에서 확인하는 수업용 프로젝트입니다.

> 이 프로젝트는 보호자의 관찰을 보조하는 실습용 프로토타입입니다. 낙상을 완전히 방지하거나 인증된 안전장치를 대체하지 않습니다.

## 구성

```text
HC-SR04 -> Raspberry Pi 5 -> nCube TAS -> Mobius -> Freeboard
                      sonic.py          oneM2M     dashboard
```

- 디바이스: Raspberry Pi 5 Model B, HC-SR04
- 디바이스 코드: Python, RPi.GPIO
- IoT 연동: nCube-Thyme-Nodejs
- oneM2M 서버: Mobius
- 대시보드: Freeboard

## 저장소 구조

```text
device/
  sonic.py                 초음파 거리 측정 및 TAS 전송
  requirements.txt
ncube/
  conf.example.js          Mobius, AE, container, TAS 설정 예시
  thyme_tas.js             nCube TAS 모듈(공개용 인증정보 제거본)
dashboard/
  jjh-sonic-dashboard.json Freeboard 대시보드 설정
scripts/
  start_freeboard_windows.cmd
docs/
  report-draft.pdf         5쪽 논문 초안
```

## HC-SR04 배선

| HC-SR04 | Raspberry Pi 5 | 코드 설정 |
|---|---|---|
| VCC | 5V, 물리 핀 2 | - |
| TRIG | 물리 핀 16 | BCM23 |
| ECHO | 물리 핀 18 | BCM24 |
| GND | 물리 핀 6 | - |

**주의:** HC-SR04 ECHO는 5V 신호입니다. Raspberry Pi GPIO에 직접 입력하지 말고 저항 분압 회로 또는 적절한 레벨 시프터로 3.3V 이하로 낮춰야 합니다.

## 기본 설정

기본 실습 구성은 다음 값을 사용합니다.

| 항목 | 값 |
|---|---|
| Mobius | `192.168.137.1:7579` |
| AE | `jjh-sonic` |
| container | `sonic` |
| TAS | `127.0.0.1:3105` |
| 최신 리소스 | `/Mobius/jjh-sonic/sonic/la` |
| Freeboard | `http://127.0.0.1:8004/` |

네트워크가 달라지면 `.env.example`을 참고하여 환경변수를 지정하거나 `ncube/conf.example.js`를 수정하세요.

## 실행 방법

### 1. Raspberry Pi 의존성 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r device/requirements.txt
```

### 2. nCube 설정

사용 중인 nCube 프로젝트에 다음 파일을 반영합니다.

- `ncube/conf.example.js`를 nCube의 `conf.js`로 복사
- `ncube/thyme_tas.js`를 TAS 모듈 위치에 복사

노트북 Mobius 주소가 다르면 `MOBIUS_HOST`를 변경합니다. 그다음 nCube 디렉터리에서 실행합니다.

```bash
node thyme.js
```

로그에서 TAS가 `3105` 포트로 대기하는지 확인합니다.

### 3. 초음파 측정 실행

```bash
python3 device/sonic.py
```

정상 동작 시 터미널에 거리값이 출력되고 `sonic` container에 contentInstance가 생성됩니다.

### 4. Mobius 리소스 확인

최신 값의 기본 경로는 다음과 같습니다.

```text
http://192.168.137.1:7579/Mobius/jjh-sonic/sonic/la
```

oneM2M 요청에는 `X-M2M-RI`, `X-M2M-Origin`, `Accept: application/json` 헤더가 필요합니다.

### 5. Freeboard 실행

원본 Freeboard 배포본 루트에 `dashboard/jjh-sonic-dashboard.json`을 복사한 다음 정적 서버를 실행합니다.

```powershell
py -m http.server 8004 --bind 127.0.0.1 --directory C:\path\to\freeboard-master
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:8004/index.html?load=jjh-sonic-dashboard.json
```

Windows에서는 `FREEBOARD_DIR`과 필요시 `MOBIUS_DIR`을 지정한 뒤 `scripts/start_freeboard_windows.cmd`를 사용할 수 있습니다.

## 확인된 결과와 한계

- 근거리 손 측정값 약 `4.9cm`
- Freeboard 표시 예시 `102.2cm`
- 반사 대상이 유효 범위를 벗어나면 약 `204~207cm`로 급변하는 현상 관찰
- 약 40cm 안쪽에서는 비교적 자연스럽게 추적되지만 반사 각도와 재질에 따라 ECHO가 누락될 수 있음

실제 알림 서비스에서는 단일 측정값만 사용하지 말고 중앙값 필터, 비정상 급변 제거, 위험 상태 지속시간 조건을 함께 적용하는 것이 좋습니다.

## 구현 범위

현재 구현 완료 범위는 거리 측정, nCube 전송, Mobius 저장, 리소스 조회, Freeboard 시각화까지입니다. 스마트폰 푸시 알림은 향후 확장 항목입니다.

## 보고서

현재 5쪽 논문 초안은 [`docs/report-draft.pdf`](docs/report-draft.pdf)에 있습니다. 학번, 최종 YouTube 데모 URL, GitHub URL을 넣은 뒤 제출본으로 교체해야 합니다.

