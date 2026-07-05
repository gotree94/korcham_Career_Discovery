# Day 2 · Step 10 — STL 출력 + 슬라이싱

**소요시간**: 1h  
**목표**: 설계한 부품을 3D프린터 출력용 STL 파일로 내보내고, 슬라이싱 소프트웨어에서 프린터 설정을 구성한다.

---

## 1. STL 파일이란?

**STL (Standard Tessellation Language)** : 3D 표면을 삼각형 메시로 표현한 파일 형식

```
원본 CAD 모델  →  STL 변환  →  슬라이싱  →  G-code  →  3D프린터 출력
(정확한 곡면)      (삼각형 근사)    (레이어 분할)    (명령어)
```

> STL은 3D프린터의 표준 입력 형식이다.
> FreeCAD에서 STL로 내보낼 때 **해상도**를 설정할 수 있다.

---

## 2. STL 내보내기

### 2-1: 내보낼 부품 확인

| 부품 | STL 파일명 | 권장 해상도 |
|------|-----------|:----------:|
| 베이스 플레이트 | `base_plate.stl` | 0.05mm |
| 상판 | `top_plate.stl` | 0.05mm |
| 모터 마운트 (좌) | `motor_mount_l.stl` | 0.02mm |
| 모터 마운트 (우) | `motor_mount_r.stl` | 0.02mm |
| 바퀴 본체 | `wheel_body.stl` | 0.02mm |
| 타이어 | `tire_solid.stl` | 0.05mm |
| 볼 캐스터 브라켓 | `ball_caster.stl` | 0.02mm |
| LiDAR 마운트 | `lidar_mount.stl` | 0.05mm |

### 2-2: 내보내기 방법

**방법 A — 단일 Body 내보내기**

```
1. 조합보기에서 내보낼 Body 선택 (예: Base_Plate)
2. File → Export
3. 파일 형식: "STL Mesh (*.stl)" 선택
4. 파일명 입력 → 저장
5. STL 내보내기 대화상자:
   - Deviation: "0.05 mm" (작을수록 정밀, 클수록 파일 작음)
   - OK
```

**방법 B — 메시 변환 후 내보내기 (더 세밀한 제어)**

```
1. 작업대 → "Mesh Design" 전환
2. 조합보기에서 Body 선택
3. Meshes → Create Mesh from Shape
4. Meshing Parameters:
   - Maximum Edge Length: "0.5 mm" (작을수록 정밀)
   - OK
5. 생성된 Mesh 객체 선택
6. File → Export → STL
```

### 2-3: 내보내기 팁

| 상황 | 해결 |
|------|------|
| STL 파일이 너무 큼 (100MB+) | Deviation 값을 0.1mm로 증가 |
| 곡면이 계단처럼 보임 | Deviation 값을 0.02mm로 감소 |
| 구멍이 메워져서 나옴 | FreeCAD STL 내보내기 옵션 확인, Mesh Design 경유 |
| Body가 비어서 나옴 | Body가 숨김(Hidden) 상태인지 확인 |

---

## 3. 슬라이싱 소프트웨어 (Ultimaker Cura)

### 3-1: Cura 설치

```
https://ultimaker.com/software/ultimaker-cura
→ Free Download → 설치 (기본 설정 사용)
```

> 포터블 버전도 사용 가능

### 3-2: 프린터 설정 추가

```
1. Cura 실행
2. Settings → Printer → Add Printer
3. "Creality Ender 3" 선택 (또는 실제 사용 프린터)
4. Printer Settings:
   - Build Volume: 220 × 220 × 250mm (Ender 3 기준)
   - Nozzle Size: 0.4mm
   - Material: PLA 또는 ABS
```

### 3-3: STL 불러오기

```
File → Open File → "base_plate.stl" 선택

→ 3D 뷰에 모델이 나타남
→ 이동/회전/크기 조절 도구로 플랫폼 위에 배치
```

---

## 4. 슬라이싱 설정

### 4-1: 기본 설정 권장값

| 설정 | 권장값 | 설명 |
|------|-------|------|
| Layer Height | 0.2mm | 출력 품질과 속도 균형 |
| Initial Layer Height | 0.3mm | 베드 밀착용 첫 레이어 두께 |
| Wall Thickness | 1.2mm (3겹) | 외벽 두께 |
| Infill Density | 20% | 내부 채움률 (높을수록 강함) |
| Infill Pattern | Grid 또는 Gyroid | 채움 패턴 |
| Printing Temperature | 200°C (PLA) / 230°C (ABS) | 노즐 온도 |
| Build Plate Temp | 60°C (PLA) / 100°C (ABS) | 베드 온도 |
| Print Speed | 50mm/s | 출력 속도 |
| Support | 필요 시 ON | 오버행 지지대 |
| Adhesion | Brim 또는 Raft | 베드 밀착 보조 |

### 4-2: 설정 예시 (베이스 플레이트)

```
Layer Height: 0.2mm
Wall Thickness: 1.2mm
Infill: 20%
Support: OFF (베이스는 평평하므로 불필요)
Adhesion: Brim (넓은 면적이라 Brim 추천)

Estimated Print Time: ~4시간 30분
Material Usage: ~35g
```

### 4-3: 설정 예시 (모터 마운트 — 정밀 필요)

```
Layer Height: 0.16mm (더 정밀)
Wall Thickness: 1.2mm
Infill: 30% (강도 확보)
Support: ON (구멍 내부 오버행)
Adhesion: Skirt

Estimated Print Time: ~1시간 30분
Material Usage: ~8g
```

### 4-4: G-code 생성

```
Slice 버튼 클릭 (오른쪽 하단)

→ 슬라이싱 진행 (10~30초)
→ 미리보기에서 각 레이어 확인 가능
→ "Save to Removable Drive" → SD카드에 G-code 저장
```

---

## 5. 부품별 출력 시간 예상

| 부품 | 예상 시간 | 필라멘트 | 비고 |
|------|:---------:|:---------:|------|
| Base Plate | ~4.5h | ~35g | 가장 큰 부품 |
| Top Plate | ~3h | ~20g | 얇으므로 빠름 |
| Motor Mount (1개) | ~1.5h | ~8g | 정밀도 중요 |
| Wheel Body | ~2h | ~12g | 2개 필요 |
| Tire (TPU) | ~1h | ~5g | TPU 필라멘트 별도 |
| Ball Caster Bracket | ~1h | ~6g | |
| LiDAR Mount | ~2h | ~10g | |

> **총 예상 출력 시간**: 약 16~20시간 (모든 부품)
> 실제 교육 환경에서는 **팀당 1~2개 핵심 부품**을 출력하고 나머지는 강사가 사전 출력.

---

## 6. 문제해결

| 문제 | 원인 | 해결 |
|------|------|------|
| 모델이 바닥에 안 붙음 | 베드 레벨링 불량 | 수동 레벨링 재조정 |
| 첫 레이어 안 나옴 | 노즐과 베드 간격 좁음 | Z-offset 증가 |
| 필라멘트 안 나옴 | 노즐 막힘 | Cold pull 또는 바늘 청소 |
| 출력물이 벌어짐 | 베드 온도 낮음 | 온도 5~10°C 증가 |
| 표면 거침 | 레이어 높이 큼 | 0.2mm → 0.16mm 감소 |
| 오버행 처짐 | 서포트 부족 | Support ON 또는 각도 조절 |

---

## ✅ Step 10 완료 체크리스트

- [ ] 모든 부품을 STL 파일로 내보냈다
- [ ] Cura 또는 슬라이싱 소프트웨어가 설치되었다
- [ ] 프린터 설정(노즐/베드/재질)을 구성했다
- [ ] 베이스 플레이트의 슬라이싱 설정을 완료했다
- [ ] G-code를 생성하여 저장했다
- [ ] 예상 출력 시간과 필라멘트 사용량을 확인했다
