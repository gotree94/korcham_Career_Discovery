# -*- coding: utf-8 -*-
"""
보고서 자동 생성 매크로

실행 방법:
    FreeCAD에서 이 파일을 열고: 매크로 > 매크로 실행(F5)
    또는 FreeCAD 콘솔에서:
        exec(open(r"C:\\Users\\Administrator\\Downloads\\py\\src\\15_report_generator.py").read())

설명:
    부품의 3D 모델 정보를 HTML 보고서로 자동 생성합니다.
    치수, 부피, 표면적, 재료 정보 등을 포함한 형식화된 보고서를 생성합니다.

사용법:
    1. 아래 변수들에 원하는 경로를 설정하세요.
    2. FreeCAD에서 이 매크로를 실행합니다.
    3. 지정된 출력 경로에 HTML 보고서가 생성됩니다.
"""

import os
import sys
import time
import datetime
import FreeCAD

# ======================== 사용자 설정 ========================
# 분석할 파일이 있는 디렉토리 경로
입력_디렉토리 = r"C:\Users\Administrator\Downloads\py\fcstd"

# HTML 보고서 출력 경로
보고서_출력_경로 = r"C:\Users\Administrator\Downloads\py\report\부품_보고서.html"

# 검색할 파일 확장자
파일_확장자 = ".FCStd"

# 하위 디렉토리 포함 여부
하위_디렉토리_포함 = True

# 재료명 매핑 (파일명 키워드 기반)
재료_매핑 = {
    "steel": {"이름": "강재 (Steel)", "밀도": 7.85, "색상": "#888888"},
    "aluminum": {"이름": "알루미늄 (Aluminum)", "밀도": 2.70, "색상": "#C0C0C0"},
    "aluminium": {"이름": "알루미늄 (Aluminum)", "밀도": 2.70, "색상": "#C0C0C0"},
    "plastic": {"이름": "플라스틱 (Plastic)", "밀도": 1.20, "색상": "#FFCC00"},
    "rubber": {"이름": "고무 (Rubber)", "밀도": 1.50, "색상": "#333333"},
    "copper": {"이름": "구리 (Copper)", "밀도": 8.96, "색상": "#B87333"},
    "brass": {"이름": "황동 (Brass)", "밀도": 8.50, "색상": "#CD9B1D"},
    "stainless": {"이름": "스테인리스강", "밀도": 7.93, "색상": "#D0D0D0"},
    "wood": {"이름": "목재 (Wood)", "밀도": 0.60, "색상": "#8B4513"},
    "titanium": {"이름": "티타늄 (Titanium)", "밀도": 4.51, "색상": "#A0A0A0"},
    "nylon": {"이름": "나일론 (Nylon)", "밀도": 1.15, "색상": "#F5F5DC"},
    "glass": {"이름": "유리 (Glass)", "밀도": 2.50, "색상": "#E0F0FF"},
    "carbon": {"이름": "카본 (Carbon)", "밀도": 1.80, "색상": "#2C2C2C"},
    "ceramic": {"이름": "세라믹 (Ceramic)", "밀도": 3.00, "색상": "#F5F5F5"},
}
# =============================================================


def 디렉토리_존재_확인(경로):
    """지정된 디렉토리가 존재하는지 확인하고, 없으면 생성합니다."""
    if not os.path.isdir(경로):
        try:
            os.makedirs(경로)
            print("[정보] 디렉토리를 생성했습니다: {}".format(경로))
            return True
        except OSError as 오류:
            print("[오류] 디렉토리를 생성할 수 없습니다: {} - {}".format(경로, 오류))
            return False
    return True


def fcstd_파일_검색(루트_경로, 하위_포함=True):
    """
    지정된 디렉토리에서 .FCStd 파일 목록을 검색합니다.

    Args:
        루트_경로: 검색할 시작 디렉토리
        하위_포함: 하위 디렉토리 포함 여부

    Returns:
        찾은 .FCStd 파일의 전체 경로 리스트
    """
    찾은_파일들 = []

    if 하위_포함:
        for 디렉토리_경로, 하위_디렉토리들, 파일_이름들 in os.walk(루트_경로):
            for 파일_이름 in 파일_이름들:
                if 파일_이름.lower().endswith(파일_확장자.lower()):
                    전체_경로 = os.path.join(디렉토리_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)
    else:
        if os.path.isdir(루트_경로):
            for 파일_이름 in os.listdir(루트_경로):
                if 파일_이름.lower().endswith(파일_확장자.lower()):
                    전체_경로 = os.path.join(루트_경로, 파일_이름)
                    찾은_파일들.append(전체_경로)

    return 찾은_파일들


def 파일명에서_재료_추출(파일명):
    """파일명에서 재료 정보를 추출합니다."""
    파일명_소문자 = 파일명.lower()

    for 키워드, 재료정보 in 재료_매핑.items():
        if 키워드 in 파일명_소문자:
            return 재료정보

    return {"이름": "미지정", "밀도": 0.0, "색상": "#CCCCCC"}


def 문서_정보_추출(파일_경로):
    """
    .FCStd 파일에서 상세 정보를 추출합니다.

    Args:
        파일_경로: .FCStd 파일 경로

    Returns:
        딕셔너리: 모델의 모든 정보
    """
    문서 = None
    정보 = {
        "객체_수": 0,
        "바운딩박스": {
            "너비": 0.0,
            "높이": 0.0,
            "깊이": 0.0
        },
        "부피": 0.0,
        "표면적": 0.0,
        "질량": 0.0,
        "객체_정보들": [],
        "형상_오류": []
    }

    try:
        문서 = FreeCAD.open(파일_경로)

        if 문서 is None:
            return 정보

        객체_목록 = list(문서.Objects)
        정보["객체_수"] = len(객체_목록)

        전체_바운딩박스 = None

        for 객체 in 객체_목록:
            try:
                if hasattr(객체, 'Shape') and 객체.Shape is not None:
                    형상 = 객체.Shape

                    # 객체별 상세 정보
                    객체_정보 = {
                        "이름": 객체.Name,
                        "유형":对象.TypeId if hasattr(객체, 'TypeId') else "알 수 없음",
                        "부피": 형상.Volume,
                        "표면적": 형상.Area,
                        "중심": {
                            "x": 형상.CenterOfGravity.x,
                            "y": 형상.CenterOfGravity.y,
                            "z": 형상.CenterOfGravity.z,
                        }
                    }

                    # 바운딩 박스 업데이트
                    if 전체_바운딩박스 is None:
                        전체_바운딩박스 = 형상.BoundBox
                    else:
                        전체_바운딩박스 = 전체_바운딩박스.united(형상.BoundBox)

                    정보["부피"] += 형상.Volume
                    정보["표면적"] += 형상.Area
                    정보["객체_정보들"].append(객체_정보)

            except Exception as 형상_오류:
                정보["형상_오류"].append({
                    "객체명":对象.Name,
                    "오류": str(형상_오류)
                })
                continue

        # 바운딩 박스 치수 저장
        if 전체_바운딩박스 is not None:
            정보["바운딩박스"] = {
                "너비": 전체_바운딩박스.XLength,
                "높이": 전체_바운딩박스.YLength,
                "깊이": 전체_바운딩박스.ZLength
            }

        FreeCAD.closeDocument(문서.Name)

    except Exception as 오류:
        print("  [경고] 정보 추출 실패 ({}): {}".format(파일_경로, 오류))
        if 문서 is not None:
            try:
                FreeCAD.closeDocument(문서.Name)
            except:
                pass

    return 정보


def HTML_보고서_생성(부품_데이터_목록, 출력_경로):
    """
    수집된 부품 데이터를 HTML 보고서로 생성합니다.

    Args:
        부품_데이터_목록: 각 부품별 정보 리스트
        출력_경로: HTML 파일 출력 경로

    Returns:
        bool: 성공 여부
    """

    현재_시간 = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    총_부품_수 = len(부품_데이터_목록)

    # 총 부피, 표면적 합계 계산
    총_부피 = sum(데이터["부피"] for 데이터 in 부품_데이터_목록)
    총_표면적 = sum(데이터["표면적"] for 데이터 in 부품_데이터_목록)

    # HTML 템플릿 시작
    HTML_내용 = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>부품 보고서 - FreeCAD 자동 생성</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Malgun Gothic', '맑은 고딕', 'Apple SD Gothic Neo', sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1a5276, #2e86c1);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
        }
        .header .meta {
            font-size: 0.95em;
            opacity: 0.9;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .summary-card {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 5px rgba(0,0,0,0.08);
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #1a5276;
        }
        .summary-card .label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        .content {
            padding: 30px 40px;
        }
        .section-title {
            font-size: 1.5em;
            color: #1a5276;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #2e86c1;
        }
        .part-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        }
        .part-card-header {
            background: #2e86c1;
            color: white;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .part-card-header h3 {
            font-size: 1.1em;
        }
        .part-card-body {
            padding: 25px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }
        .info-item {
            padding: 12px 16px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #2e86c1;
        }
        .info-item .key {
            font-size: 0.85em;
            color: #666;
            margin-bottom: 4px;
        }
        .info-item .val {
            font-size: 1.1em;
            font-weight: 600;
            color: #333;
        }
        .object-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
        }
        .object-table th {
            background: #eaf2f8;
            color: #1a5276;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
        }
        .object-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #eee;
        }
        .object-table tr:hover {
            background: #f5f8fc;
        }
        .footer {
            background: #2c3e50;
            color: #bdc3c7;
            text-align: center;
            padding: 25px;
            font-size: 0.9em;
        }
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }
        .badge-info {
            background: #d4efdf;
            color: #1e8449;
        }
        .material-badge {
            background: #ebf5fb;
            color: #2e86c1;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FreeCAD 부품 보고서</h1>
            <div class="meta">
                자동 생성 일시: {보고서_일시} | 생성 도구: FreeCAD Python 매크로
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="value">{총_부품_수}</div>
                <div class="label">총 부품 수</div>
            </div>
            <div class="summary-card">
                <div class="value">{총_부피:,.1f}</div>
                <div class="label">총 부피 (mm³)</div>
            </div>
            <div class="summary-card">
                <div class="value">{총_표면적:,.1f}</div>
                <div class="label">총 표면적 (mm²)</div>
            </div>
            <div class="summary-card">
                <div class="value">{총_객체_수}</div>
                <div class="label">총 객체 수</div>
            </div>
        </div>

        <div class="content">
            <h2 class="section-title">부품 상세 정보</h2>
""".format(
        보고서_일시=현재_시간,
        총_부품_수=총_부품_수,
        총_부피=총_부피,
        총_표면적=총_표면적,
        총_객체_수=sum(데이터["객체_수"] for 데이터 in 부품_데이터_목록)
    )

    # 각 부품별 상세 정보 추가
    for 순번, 데이터 in enumerate(부품_데이터_목록, 1):
        파일명 = 데이터["파일명"]
        재료 = 데이터["재료"]

        # 객체 테이블 행 생성
        객체_테이블_행 = ""
        for 객체 in 데이터["객체_정보들"]:
            객체_테이블_행 += """
                <tr>
                    <td>{이름}</td>
                    <td>{유형}</td>
                    <td>{부피:.2f}</td>
                    <td>{표면적:.2f}</td>
                    <td>({x:.2f}, {y:.2f}, {z:.2f})</td>
                </tr>""".format(
                이름=객체["이름"],
                유형=객체["유형"],
                부피=객체["부피"],
                표면적=객체["표면적"],
                x=객체["중심"]["x"],
                y=객체["중심"]["y"],
                z=객체["중심"]["z"]
            )

        # 추정 질량 계산
        추정_질량 = 데이터["부피"] * 재료["밀도"] / 1000.0  # g 단위

        HTML_내용 += """
            <div class="part-card">
                <div class="part-card-header">
                    <h3>#{순번} {파일명}</h3>
                    <span class="material-badge">{재료명}</span>
                </div>
                <div class="part-card-body">
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="key">파일명</div>
                            <div class="val">{파일명}</div>
                        </div>
                        <div class="info-item">
                            <div class="key">객체 수</div>
                            <div class="val">{객체_수}개</div>
                        </div>
                        <div class="info-item">
                            <div class="key">너비 (X)</div>
                            <div class="val">{너비:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">높이 (Y)</div>
                            <div class="val">{높이:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">깊이 (Z)</div>
                            <div class="val">{깊이:.2f} mm</div>
                        </div>
                        <div class="info-item">
                            <div class="key">부피</div>
                            <div class="val">{부피:.2f} mm³</div>
                        </div>
                        <div class="info-item">
                            <div class="key">표면적</div>
                            <div class="val">{표면적:.2f} mm²</div>
                        </div>
                        <div class="info-item">
                            <div class="key">추정 질량</div>
                            <div class="val">{질량:.2f} g</div>
                        </div>
                        <div class="info-item">
                            <div class="key">재료</div>
                            <div class="val">{재료명}</div>
                        </div>
                        <div class="info-item">
                            <div class="key">밀도</div>
                            <div class="val">{밀도} g/cm³</div>
                        </div>
                    </div>

                    <h4 style="margin-top: 25px; color: #1a5276;">객체 상세 목록</h4>
                    <table class="object-table">
                        <thead>
                            <tr>
                                <th>객체명</th>
                                <th>유형</th>
                                <th>부피 (mm³)</th>
                                <th>표면적 (mm²)</th>
                                <th>무게중심 (mm)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {객체_테이블}
                        </tbody>
                    </table>
                </div>
            </div>
""".format(
            순번=순번,
            파일명=파일명,
            재료명=재료["이름"],
            객체_수=데이터["객체_수"],
            너비=데이터["바운딩박스"]["너비"],
            높이=데이터["바운딩박스"]["높이"],
            깊이=데이터["바운딩박스"]["깊이"],
            부피=데이터["부피"],
            표면적=데이터["표면적"],
            질량=추정_질량,
            밀도=재료["밀도"],
            객체_테이블=객체_테이블_행
        )

    # HTML 템플릿 마무리
    HTML_내용 += """
        </div>

        <div class="footer">
            <p>이 보고서는 FreeCAD Python 매크로에 의해 자동 생성되었습니다.</p>
            <p>생성 일시: {보고서_일시} | FreeCAD Python + AI 설계 자동화</p>
        </div>
    </div>
</body>
</html>""".format(보고서_일시=현재_시간)

    # HTML 파일 저장
    try:
        출력_디렉토리 = os.path.dirname(출력_경로)
        디렉토리_존재_확인(출력_디렉토리)

        with open(출력_경로, 'w', encoding='utf-8') as HTML_파일:
            HTML_파일.write(HTML_내용)

        return True

    except Exception as 오류:
        print("[오류] HTML 보고서 저장 실패: {}".format(오류))
        return False


def 보고서_자동_생성_실행():
    """보고서 자동 생성의 전체 프로세스를 실행합니다."""

    print("=" * 65)
    print("  부품 보고서 자동 생성 시작")
    print("=" * 65)
    print("  입력 디렉토리 : {}".format(입력_디렉토리))
    print("  보고서 출력   : {}".format(보고서_출력_경로))
    print("  하위 디렉토리 : {}".format("포함" if 하위_디렉토리_포함 else "미포함"))
    print("-" * 65)

    # 디렉토리 존재 확인
    if not os.path.isdir(입력_디렉토리):
        print("[실패] 입력 디렉토리가 없습니다. 경로를 확인하세요.")
        return

    # .FCStd 파일 검색
    print("\n[1단계] .FCStd 파일 검색 중...")
    찾은_파일들 = fcstd_파일_검색(입력_디렉토리, 하위_디렉토리_포함)
    전체_파일_수 = len(찾은_파일들)

    if 전체_파일_수 == 0:
        print("[정보] 검색된 .FCStd 파일이 없습니다.")
        return

    print("  -> 총 {} 개의 파일을 찾았습니다.".format(전체_파일_수))

    # 부품 정보 수집
    print("\n[2단계] 부품 정보 수집 중...")
    시작_시간 = time.time()
    부품_데이터_목록 = []
    성공_수 = 0
    실패_수 = 0

    for 순번, 파일_경로 in enumerate(찾은_파일들, 1):
        진행률 = (순번 / 전체_파일_수) * 100
        파일명 = os.path.basename(파일_경로)
        상대_경로 = os.path.relpath(파일_경로, 입력_디렉토리)

        print("  [{:5.1f}%] ({}/{}) 정보 수집: {}".format(
            진행률, 순번, 전체_파일_수, 상대_경로))

        try:
            # 문서 정보 추출
            문서_정보 = 문서_정보_추출(파일_경로)

            # 재료 정보 추출
            재료 = 파일명에서_재료_추출(파일명)

            # 부품 데이터 구성
            부품_데이터 = {
                "파일명": 파일명,
                "상대_경로": 상대_경로,
                "객체_수": 문서_정보["객체_수"],
                "바운딩박스": 문서_정보["바운딩박스"],
                "부피": 문서_정보["부피"],
                "표면적": 문서_정보["표면적"],
                "재료": 재료,
                "객체_정보들": 문서_정보["객체_정보들"]
            }

            부품_데이터_목록.append(부품_데이터)
            성공_수 += 1

            추정_질량 = 문서_정보["부피"] * 재료["밀도"] / 1000.0
            print("    -> 객체: {}, 부피: {:.1f}mm³, 추정 질량: {:.1f}g, 재료: {}".format(
                문서_정보["객체_수"],
                문서_정보["부피"],
                추정_질량,
                재료["이름"]
            ))

        except Exception as 수집_오류:
            print("    [오류] 정보 수집 실패: {}".format(수집_오류))
            실패_수 += 1

    # HTML 보고서 생성
    print("\n[3단계] HTML 보고서 생성 중...")
    if HTML_보고서_생성(부품_데이터_목록, 보고서_출력_경로):
        print("  -> HTML 보고서 생성 완료: {}".format(보고서_출력_경로))
    else:
        print("  -> HTML 보고서 생성 실패!")
        return

    # 결과 요약
    종료_시간 = time.time()
    총_소요_시간 = 종료_시간 - 시작_시간

    print("\n" + "=" * 65)
    print("  보고서 자동 생성 완료")
    print("=" * 65)
    print("  총 파일 수    : {}".format(전체_파일_수))
    print("  성공          : {}".format(성공_수))
    print("  실패          : {}".format(실패_수))
    print("  총 소요 시간  : {:.2f}초".format(총_소요_시간))
    print("  출력 파일     : {}".format(보고서_출력_경로))

    if 부품_데이터_목록:
        총_부피 = sum(데이터["부피"] for 데이터 in 부품_데이터_목록)
        총_표면적 = sum(데이터["표면적"] for 데이터 in 부품_데이터_목록)
        print("  총 부피       : {:,.2f} mm³".format(총_부피))
        print("  총 표면적     : {:,.2f} mm²".format(총_표면적))

    print("=" * 65)


# ======================== 실행 ========================
if __name__ == "__main__":
    보고서_자동_생성_실행()
else:
    # FreeCAD에서 직접 실행할 때
    보고서_자동_생성_실행()
