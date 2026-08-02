# -*- coding: utf-8 -*-
"""
Part 7 - 38: 버전 관리 시스템 매크로

FreeCAD 설계 파일의 버전 관리를 위한 매크로.
스냅샷 생성, 버전 비교, 변경 이력 관리 등을 수행.
로컬 파일 기반의 간이 버전 관리 시스템.

사용법: FreeCAD에서 실행하여 설계 버전을 관리.
"""

import sys
import os
import time
import hashlib
import json
import shutil

try:
    import FreeCAD
    import Part
    from FreeCAD import Base
except ImportError:
    print("[오류] FreeCAD 모듈을 찾을 수 없습니다.")
    sys.exit(1)


# ============================================================
# 모델 스냅샷 클래스
# ============================================================

class ModelSnapshot:
    """
    3D 모델의 스냅샷을 관리하는 클래스.
    """

    def __init__(self, name, shape=None, description=""):
        """
        매개변수:
            name (str): 스냅샷 이름
            shape (Part.Shape): 스냅샷할 형태
            description (str): 설명
        """
        self.name = name
        self.description = description
        self.timestamp = time.time()
        self.shape_hash = ""
        self.bounding_box = None
        self.volume = 0.0
        self.filepath = ""

        if shape is not None:
            self._analyze_shape(shape)

    def _analyze_shape(self, shape):
        """형태를 분석하여 특성을 추출한다."""
        try:
            self.bounding_box = shape.BoundBox
            self.volume = shape.Volume

            # 형태 해시 (메모리 주소 기반 대신 크기/부피 사용)
            hash_input = f"{self.bounding_box.XLength}:{self.bounding_box.YLength}:{self.bounding_box.ZLength}:{self.volume}"
            self.shape_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        except Exception as e:
            print(f"[경고] 형태 분석 실패: {e}")

    def to_dict(self):
        """딕셔너리로 변환한다."""
        return {
            "name": self.name,
            "description": self.description,
            "timestamp": self.timestamp,
            "shape_hash": self.shape_hash,
            "bounding_box": {
                "x": self.bounding_box.XLength if self.bounding_box else 0,
                "y": self.bounding_box.YLength if self.bounding_box else 0,
                "z": self.bounding_box.ZLength if self.bounding_box else 0,
            } if self.bounding_box else None,
            "volume": self.volume,
            "filepath": self.filepath,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 생성한다."""
        snapshot = cls(data["name"])
        snapshot.description = data.get("description", "")
        snapshot.timestamp = data.get("timestamp", 0)
        snapshot.shape_hash = data.get("shape_hash", "")
        snapshot.volume = data.get("volume", 0.0)
        snapshot.filepath = data.get("filepath", "")

        if data.get("bounding_box"):
            bb = data["bounding_box"]
            snapshot.bounding_box = Base.BoundBox(
                0, 0, 0,
                bb.get("x", 0), bb.get("y", 0), bb.get("z", 0)
            )

        return snapshot


# ============================================================
# 버전 관리 클래스
# ============================================================

class VersionManager:
    """
    FreeCAD 설계 파일의 버전을 관리하는 클래스.
    """

    def __init__(self, project_name, base_dir=None):
        """
        매개변수:
            project_name (str): 프로젝트 이름
            base_dir (str): 기본 저장 디렉토리
        """
        self.project_name = project_name
        self.base_dir = base_dir or os.path.join(os.path.expanduser("~"), "freecad_versions")
        self.project_dir = os.path.join(self.base_dir, project_name)
        self.metadata_file = os.path.join(self.project_dir, "metadata.json")
        self.snapshots = []

        # 프로젝트 디렉토리 생성
        os.makedirs(self.project_dir, exist_ok=True)

        # 기존 메타데이터 로드
        self._load_metadata()

    def _load_metadata(self):
        """메타데이터를 로드한다."""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.snapshots = [ModelSnapshot.from_dict(s) for s in data.get("snapshots", [])]
                print(f"[정보] 기존 버전 {len(self.snapshots)}개 로드됨")
            except Exception as e:
                print(f"[경고] 메타데이터 로드 실패: {e}")
                self.snapshots = []
        else:
            self.snapshots = []

    def _save_metadata(self):
        """메타데이터를 저장한다."""
        data = {
            "project_name": self.project_name,
            "snapshot_count": len(self.snapshots),
            "last_updated": time.time(),
            "snapshots": [s.to_dict() for s in self.snapshots],
        }

        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[오류] 메타데이터 저장 실패: {e}")

    def create_snapshot(self, name, shape=None, description=""):
        """
        새 스냅샷을 생성한다.

        매개변수:
            name (str): 스냅샷 이름
            shape (Part.Shape): 스냅샷할 형태
            description (str): 설명

        반환값:
            ModelSnapshot: 생성된 스냅샷
        """
        snapshot = ModelSnapshot(name, shape, description)

        # STL 파일로 저장
        if shape is not None:
            stl_filename = f"{name}_{int(snapshot.timestamp)}.stl"
            stl_path = os.path.join(self.project_dir, stl_filename)

            try:
                mesh = Part.Mesh()
                if hasattr(shape, "Shapes"):
                    for s in shape.Shapes:
                        mesh.addMesh(s.tessellate(0.5))
                else:
                    mesh.addMesh(shape.tessellate(0.5))
                mesh.write(stl_path)
                snapshot.filepath = stl_path
                print(f"[정보] STL 파일 저장: {stl_filename}")
            except Exception as e:
                print(f"[오류] STL 저장 실패: {e}")

        self.snapshots.append(snapshot)
        self._save_metadata()

        print(f"[정보] 스냅샷 '{name}' 생성 완료 (총 {len(self.snapshots)}개)")
        return snapshot

    def list_snapshots(self):
        """
        모든 스냅샷을 출력한다.

        반환값:
            list: 스냅샷 목록
        """
        print(f"\n[정보] === {self.project_name} 스냅샷 목록 ===")

        if not self.snapshots:
            print("  스냅샷이 없습니다.")
            return []

        for idx, snapshot in enumerate(self.snapshots, 1):
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snapshot.timestamp))
            print(f"  {idx}. {snapshot.name} ({ts})")
            print(f"     설명: {snapshot.description or '없음'}")
            if snapshot.bounding_box:
                bb = snapshot.bounding_box
                print(f"     크기: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
            print(f"     부피: {snapshot.volume:.1f} mm³")
            print(f"     해시: {snapshot.shape_hash}")
            print()

        return self.snapshots

    def get_snapshot(self, index):
        """
        지정된 인덱스의 스냅샷을 반환한다.

        매개변수:
            index (int): 스냅샷 인덱스 (0부터 시작)

        반환값:
            ModelSnapshot: 스냅샷
        """
        if 0 <= index < len(self.snapshots):
            return self.snapshots[index]
        print(f"[오류] 잘못된 인덱스: {index}")
        return None

    def compare_snapshots(self, index1, index2):
        """
        두 스냅샷을 비교한다.

        매개변수:
            index1 (int): 첫 번째 스냅샷 인덱스
            index2 (int): 두 번째 스냅샷 인덱스

        반환값:
            dict: 비교 결과
        """
        if index1 >= len(self.snapshots) or index2 >= len(self.snapshots):
            print("[오류] 잘못된 인덱스")
            return None

        snap1 = self.snapshots[index1]
        snap2 = self.snapshots[index2]

        print(f"\n[정보] === 스냅샷 비교 ===")
        print(f"  {snap1.name} vs {snap2.name}")

        # 크기 비교
        if snap1.bounding_box and snap2.bounding_box:
            bb1 = snap1.bounding_box
            bb2 = snap2.bounding_box
            print(f"\n  크기 변화:")
            print(f"    X: {bb1.XLength:.1f} → {bb2.XLength:.1f} mm ({bb2.XLength - bb1.XLength:+.1f}mm)")
            print(f"    Y: {bb1.YLength:.1f} → {bb2.YLength:.1f} mm ({bb2.YLength - bb1.YLength:+.1f}mm)")
            print(f"    Z: {bb1.ZLength:.1f} → {bb2.ZLength:.1f} mm ({bb2.ZLength - bb1.ZLength:+.1f}mm)")

        # 부피 비교
        vol_diff = snap2.volume - snap1.volume
        vol_pct = (vol_diff / snap1.volume * 100) if snap1.volume > 0 else 0
        print(f"\n  부피 변화: {snap1.volume:.1f} → {snap2.volume:.1f} mm³ ({vol_diff:+.1f}mm³, {vol_pct:+.1f}%)")

        # 동일성 확인
        is_same = snap1.shape_hash == snap2.shape_hash
        print(f"\n  동일성: {'동일' if is_same else '다름'}")

        return {
            "name1": snap1.name,
            "name2": snap2.name,
            "size_change": {
                "x": bb2.XLength - bb1.XLength if snap1.bounding_box and snap2.bounding_box else 0,
                "y": bb2.YLength - bb1.YLength if snap1.bounding_box and snap2.bounding_box else 0,
                "z": bb2.ZLength - bb1.ZLength if snap1.bounding_box and snap2.bounding_box else 0,
            },
            "volume_change": vol_diff,
            "volume_change_pct": vol_pct,
            "is_same": is_same,
        }

    def delete_snapshot(self, index):
        """
        스냅샷을 삭제한다.

        매개변수:
            index (int): 삭제할 스냅샷 인덱스

        반환값:
            bool: 성공 여부
        """
        if index < 0 or index >= len(self.snapshots):
            print(f"[오류] 잘못된 인덱스: {index}")
            return False

        snapshot = self.snapshots[index]

        # STL 파일 삭제
        if snapshot.filepath and os.path.exists(snapshot.filepath):
            try:
                os.remove(snapshot.filepath)
                print(f"[정보] 파일 삭제: {snapshot.filepath}")
            except Exception as e:
                print(f"[경고] 파일 삭제 실패: {e}")

        # 스냅샷 목록에서 제거
        self.snapshots.pop(index)
        self._save_metadata()

        print(f"[정보] 스냅샷 '{snapshot.name}' 삭제 완료")
        return True

    def revert_to_snapshot(self, index):
        """
        지정된 스냅샷으로 되돌린다 (STL 파일 경로 반환).

        매개변수:
            index (int): 되돌릴 스냅샷 인덱스

        반환값:
            str: STL 파일 경로
        """
        snapshot = self.get_snapshot(index)
        if snapshot is None:
            return None

        if snapshot.filepath and os.path.exists(snapshot.filepath):
            print(f"[정보] 스냅샷 '{snapshot.name}'으로 되돌리기: {snapshot.filepath}")
            return snapshot.filepath
        else:
            print(f"[오류] 스냅샷 파일을 찾을 수 없습니다: {snapshot.filepath}")
            return None

    def export_history(self, filename=None):
        """
        버전 이력을 파일로 내보낸다.

        매개변수:
            filename (str): 출력 파일 경로

        반환값:
            str: 저장된 파일 경로
        """
        if filename is None:
            filename = os.path.join(self.project_dir, "history.txt")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"프로젝트: {self.project_name}\n")
                f.write(f"스냅샷 수: {len(self.snapshots)}\n")
                f.write(f"{'=' * 60}\n\n")

                for idx, snapshot in enumerate(self.snapshots, 1):
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(snapshot.timestamp))
                    f.write(f"[{idx}] {snapshot.name}\n")
                    f.write(f"  시간: {ts}\n")
                    f.write(f"  설명: {snapshot.description or '없음'}\n")
                    if snapshot.bounding_box:
                        bb = snapshot.bounding_box
                        f.write(f"  크기: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm\n")
                    f.write(f"  부피: {snapshot.volume:.1f} mm³\n")
                    f.write(f"  해시: {snapshot.shape_hash}\n")
                    f.write(f"  파일: {snapshot.filepath or '없음'}\n\n")

            print(f"[정보] 이력 내보내기 완료: {filename}")
            return filename
        except Exception as e:
            print(f"[오류] 이력 내보내기 실패: {e}")
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
            doc = FreeCAD.newDocument("버전관리")

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
    예제 프로젝트의 버전 관리를 테스트한다.
    """
    print("=" * 60)
    print("  버전 관리 시스템 매크로 시작")
    print("=" * 60)

    # 버전 관리자 생성
    vm = VersionManager("예제설계프로젝트")

    # 스냅샷 1: 기본 상자
    print("\n[정보] 스냅샷 1: 기본 상자")
    box = Part.makeBox(100, 80, 30)
    vm.create_snapshot("v1_기본상자", box, "기본 100x80x30mm 상자")

    # 스냅샷 2: 상자 수정
    print("\n[정보] 스냅샷 2: 상자 수정")
    box2 = Part.makeBox(120, 90, 35)
    vm.create_snapshot("v2_크기증가", box2, "크기 120x90x35mm로 확대")

    # 스냅샷 3: 복합 형태
    print("\n[정보] 스냅샷 3: 복합 형태")
    cylinder = Part.makeCylinder(30, 50)
    sphere = Part.makeSphere(25, Base.Vector(0, 0, 50))
    compound = cylinder.fuse(sphere)
    vm.create_snapshot("v3_복합형태", compound, "실린더+구 복합 형태")

    # 스냅샷 목록 출력
    vm.list_snapshots()

    # 스냅샷 비교
    print("\n[정보] 스냅샷 비교 (v1 vs v2)")
    vm.compare_snapshots(0, 1)

    # 이력 내보내기
    vm.export_history()

    print(f"\n{'=' * 60}")
    print("  버전 관리 시스템 매크로 완료!")
    print(f"{'=' * 60}")


# 스크립트 직접 실행 시 자동 실행
if __name__ == "__main__":
    run()
else:
    run()
