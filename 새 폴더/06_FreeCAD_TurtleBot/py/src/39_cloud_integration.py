# -*- coding: utf-8 -*-
"""
Part 7 - 39: 클라우드 연동 매크로

FreeCAD 설계 데이터를 클라우드 서비스와 연동하는 매크로.
로컬 프로젝트 메타데이터를 관리하고, 클라우드 동기화 인터페이스를 제공.
REST API 기반 동기화 시뮬레이션 포함.

사용법: FreeCAD에서 실행하여 설계 데이터를 클라우드와 연동.
"""

import sys
import os
import time
import json
import hashlib

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 설계 데이터 클래스
# ============================================================

class DesignData:
    """
    설계 데이터를 관리하는 클래스.
    """

    def __init__(self, project_name, shape=None, metadata=None):
        """
        매개변수:
            project_name (str): 프로젝트 이름
            shape (Part.Shape): 설계 형태
            metadata (dict): 추가 메타데이터
        """
        self.project_name = project_name
        self.created_at = time.time()
        self.updated_at = time.time()
        self.version = "1.0.0"
        self.author = ""
        self.description = ""
        self.tags = []
        self.shape_hash = ""
        self.bounding_box = None
        self.volume = 0.0
        self.file_size = 0
        self.metadata = metadata or {}

        if shape is not None:
            self._analyze_shape(shape)

    def _analyze_shape(self, shape):
        """형태를 분석한다."""
        try:
            self.bounding_box = shape.BoundBox
            self.volume = shape.Volume

            hash_input = f"{self.bounding_box.XLength}:{self.bounding_box.YLength}:{self.bounding_box.ZLength}:{self.volume}"
            self.shape_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        except Exception as e:
            print(f"[경고] 형태 분석 실패: {e}")

    def to_dict(self):
        """딕셔너리로 변환한다."""
        return {
            "project_name": self.project_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "tags": self.tags,
            "shape_hash": self.shape_hash,
            "bounding_box": {
                "x": self.bounding_box.XLength if self.bounding_box else 0,
                "y": self.bounding_box.YLength if self.bounding_box else 0,
                "z": self.bounding_box.ZLength if self.bounding_box else 0,
            } if self.bounding_box else None,
            "volume": self.volume,
            "file_size": self.file_size,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 생성한다."""
        dd = cls(data["project_name"])
        dd.created_at = data.get("created_at", 0)
        dd.updated_at = data.get("updated_at", 0)
        dd.version = data.get("version", "1.0.0")
        dd.author = data.get("author", "")
        dd.description = data.get("description", "")
        dd.tags = data.get("tags", [])
        dd.shape_hash = data.get("shape_hash", "")
        dd.volume = data.get("volume", 0.0)
        dd.file_size = data.get("file_size", 0)
        dd.metadata = data.get("metadata", {})

        if data.get("bounding_box"):
            bb = data["bounding_box"]
            dd.bounding_box = Base.BoundBox(
                0, 0, 0,
                bb.get("x", 0), bb.get("y", 0), bb.get("z", 0)
            )

        return dd


# ============================================================
# 클라우드 연동 관리 클래스
# ============================================================

class CloudSyncManager:
    """
    클라우드 동기화를 관리하는 클래스.
    실제 클라우드 API 대신 로컬 시뮬레이션으로 동작.
    """

    def __init__(self, config_dir=None):
        """
        매개변수:
            config_dir (str): 설정 디렉토리 경로
        """
        self.config_dir = config_dir or os.path.join(os.path.expanduser("~"), ".freecad_cloud")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.cache_dir = os.path.join(self.config_dir, "cache")
        self.sync_log_file = os.path.join(self.config_dir, "sync_log.json")

        # 디렉토리 생성
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

        # 설정 로드
        self.config = self._load_config()
        self.sync_log = self._load_sync_log()

    def _load_config(self):
        """설정을 로드한다."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[경고] 설정 로드 실패: {e}")

        # 기본 설정
        return {
            "server_url": "https://api.freecad-cloud.example.com",
            "api_key": "",
            "auto_sync": False,
            "sync_interval": 300,
            "last_sync": 0,
        }

    def _save_config(self):
        """설정을 저장한다."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[오류] 설정 저장 실패: {e}")

    def _load_sync_log(self):
        """동기화 로그를 로드한다."""
        if os.path.exists(self.sync_log_file):
            try:
                with open(self.sync_log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"logs": []}

    def _save_sync_log(self):
        """동기화 로그를 저장한다."""
        try:
            with open(self.sync_log_file, "w", encoding="utf-8") as f:
                json.dump(self.sync_log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[오류] 동기화 로그 저장 실패: {e}")

    def configure(self, server_url, api_key, auto_sync=False):
        """
        클라우드 설정을 구성한다.

        매개변수:
            server_url (str): 서버 URL
            api_key (str): API 키
            auto_sync (bool): 자동 동기화 여부
        """
        self.config["server_url"] = server_url
        self.config["api_key"] = api_key
        self.config["auto_sync"] = auto_sync
        self._save_config()
        print(f"[정보] 클라우드 설정 저장 완료")

    def upload_design(self, design_data, filepath=None):
        """
        설계 데이터를 클라우드에 업로드한다 (시뮬레이션).

        매개변수:
            design_data (DesignData): 업로드할 설계 데이터
            filepath (str): STL 파일 경로

        반환값:
            dict: 업로드 결과
        """
        print(f"\n[정보] === 클라우드 업로드 시작 ===")
        print(f"  프로젝트: {design_data.project_name}")

        # 업로드 시뮬레이션
        result = {
            "success": True,
            "project_id": hashlib.md5(design_data.project_name.encode()).hexdigest()[:8],
            "upload_time": time.time(),
            "file_size": design_data.file_size,
            "message": "업로드 성공 (시뮬레이션)",
        }

        # 캐시에 저장
        cache_file = os.path.join(self.cache_dir, f"{design_data.project_name}.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(design_data.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[경고] 캐시 저장 실패: {e}")

        # 동기화 로그
        self.sync_log["logs"].append({
            "action": "upload",
            "project": design_data.project_name,
            "timestamp": time.time(),
            "success": True,
        })
        self._save_sync_log()

        print(f"[정보] 업로드 완료 (ID: {result['project_id']})")
        return result

    def download_design(self, project_id):
        """
        클라우드에서 설계 데이터를 다운로드한다 (시뮬레이션).

        매개변수:
            project_id (str): 프로젝트 ID

        반환값:
            DesignData: 다운로드된 설계 데이터
        """
        print(f"\n[정보] === 클라우드 다운로드 시작 ===")
        print(f"  프로젝트 ID: {project_id}")

        # 캐시에서 검색
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("project_name"):
                        design = DesignData.from_dict(data)
                        print(f"[정보] 다운로드 완료: {design.project_name}")
                        return design
                except Exception:
                    continue

        print(f"[정보] 캐시에서 프로젝트를 찾을 수 없습니다: {project_id}")
        return None

    def sync_projects(self):
        """
        모든 프로젝트를 동기화한다.

        반환값:
            dict: 동기화 결과
        """
        print(f"\n[정보] === 프로젝트 동기화 시작 ===")

        cached_files = [f for f in os.listdir(self.cache_dir) if f.endswith(".json")]
        print(f"  캐시된 프로젝트: {len(cached_files)}개")

        result = {
            "total": len(cached_files),
            "synced": 0,
            "failed": 0,
            "timestamp": time.time(),
        }

        for filename in cached_files:
            cache_file = os.path.join(self.cache_dir, filename)
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                project_name = data.get("project_name", filename)
                print(f"  동기화: {project_name}")
                result["synced"] += 1
            except Exception as e:
                print(f"  동기화 실패: {filename} - {e}")
                result["failed"] += 1

        # 로그
        self.sync_log["logs"].append({
            "action": "sync",
            "timestamp": time.time(),
            "result": result,
        })
        self._save_sync_log()

        print(f"[정보] 동기화 완료: {result['synced']}개 성공, {result['failed']}개 실패")
        return result

    def get_sync_history(self):
        """
        동기화 이력을 반환한다.

        반환값:
            list: 동기화 이력 목록
        """
        return self.sync_log.get("logs", [])


# ============================================================
# 프로젝트 관리 함수
# ============================================================

def create_project(project_name, shape=None, description="", tags=None):
    """
    새 설계 프로젝트를 생성한다.

    매개변수:
        project_name (str): 프로젝트 이름
        shape (Part.Shape): 설계 형태
        description (str): 설명
        tags (list): 태그 목록

    반환값:
        DesignData: 생성된 설계 데이터
    """
    design = DesignData(project_name, shape)
    design.description = description
    design.tags = tags or []

    print(f"[정보] 새 프로젝트 생성: {project_name}")
    return design


def save_project(design_data, directory=None):
    """
    프로젝트를 로컬에 저장한다.

    매개변수:
        design_data (DesignData): 설계 데이터
        directory (str): 저장 디렉토리

    반환값:
        str: 저장된 파일 경로
    """
    if directory is None:
        directory = os.path.join(os.path.expanduser("~"), "freecad_projects")

    os.makedirs(directory, exist_ok=True)

    filename = f"{design_data.project_name}.json"
    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(design_data.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"[정보] 프로젝트 저장: {filepath}")
        return filepath
    except Exception as e:
        print(f"[오류] 프로젝트 저장 실패: {e}")
        return None


def load_project(filepath):
    """
    프로젝트를 로컬에서 로드한다.

    매개변수:
        filepath (str): 프로젝트 파일 경로

    반환값:
        DesignData: 로드된 설계 데이터
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        design = DesignData.from_dict(data)
        print(f"[정보] 프로젝트 로드: {design.project_name}")
        return design
    except Exception as e:
        print(f"[오류] 프로젝트 로드 실패: {e}")
        return None


# ============================================================
# FreeCAD 통합 함수
# ============================================================

def add_to_freecad_document(shape, name):
    """
    형태를 FreeCAD 활성 도큐먼트에 추가한다.
    """
    try:
        doc = FreeCAD.ActiveDocument
        if doc is None:
            doc = FreeCAD.newDocument("클라우드연동")

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()
        print(f"[정보] 도큐먼트에 '{name}' 추가 완료")
        return obj
    except Exception as e:
        print(f"[오류] 도큐먼트 추가 실패: {e}")
        return None


def export_stl(shape, filename):
    """
    형태를 STL 파일로 내보낸다.
    """
    try:
        mesh = Part.Mesh()
        if hasattr(shape, "Shapes"):
            for s in shape.Shapes:
                mesh.addMesh(s.tessellate(0.5))
        else:
            mesh.addMesh(shape.tessellate(0.5))
        mesh.write(filename)
        print(f"[정보] STL 파일 저장 완료: {filename}")
        return filename
    except Exception as e:
        print(f"[오류] STL 내보내기 실패: {e}")
        return None


# ============================================================
# 메인 실행 함수
# ============================================================

def run():
    """
    메인 실행 함수.
    클라우드 연동 기능을 테스트한다.
    """
    print("=" * 60)
    print("  클라우드 연동 매크로 시작")
    print("=" * 60)

    # 클라우드 매니저 생성
    csm = CloudSyncManager()

    # 설정
    print("\n[단계 1] 클라우드 설정")
    csm.configure(
        server_url="https://api.freecad-cloud.example.com",
        api_key="test_api_key_12345",
        auto_sync=True,
    )

    # 예제 설계 데이터 생성
    print("\n[단계 2] 설계 데이터 생성")
    box = Part.makeBox(100, 80, 30)
    design1 = create_project(
        "IoT_센서케이스",
        box,
        description="ESP32용 센서 보호 케이스",
        tags=["IoT", "센서", "케이스"],
    )
    design1.author = "설계자"

    # 로컬 저장
    print("\n[단계 3] 로컬 저장")
    save_project(design1)

    # 클라우드 업로드
    print("\n[단계 4] 클라우드 업로드")
    upload_result = csm.upload_design(design1)

    # 두 번째 설계
    cylinder = Part.makeCylinder(25, 60)
    design2 = create_project(
        "로봇_암커넥터",
        cylinder,
        description="로봇 암 연결 부품",
        tags=["로봇", "커넥터"],
    )
    csm.upload_design(design2)

    # 동기화
    print("\n[단계 5] 프로젝트 동기화")
    sync_result = csm.sync_projects()

    # 이력 확인
    print("\n[단계 6] 동기화 이력")
    history = csm.get_sync_history()
    for log in history[-5:]:
        ts = time.strftime("%H:%M:%S", time.localtime(log["timestamp"]))
        print(f"  [{ts}] {log['action']} - {log.get('project', '')}")

    print(f"\n{'=' * 60}")
    print("  클라우드 연동 매크로 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()
