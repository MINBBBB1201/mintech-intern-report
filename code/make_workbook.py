"""Build the carrier seating and witness-coupon comparison workbook."""

import argparse
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description="캐리어 안착 및 witness coupon 쌍체 비교 워크북 생성")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "workbooks/carrier_coupon_comparison.xlsx")
    parser.add_argument("--runtime-root", type=Path, default=Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies", help="node/bin과 node/node_modules를 포함한 번들 의존성 폴더")
    parser.add_argument("--check-dir", type=Path, help="선택: 자동 검사와 시트 미리보기 저장 폴더")
    args = parser.parse_args()
    node = args.runtime_root / "node/bin" / ("node.exe" if os.name == "nt" else "node")
    modules = args.runtime_root / "node/node_modules"
    if not node.is_file() or not (modules / "@oai/artifact-tool").is_dir():
        parser.error("Node.js와 @oai/artifact-tool이 필요합니다. --runtime-root에 번들 의존성 경로를 지정하세요.")
    command = [str(node), str(Path(__file__).with_suffix(".mjs")), "--out", str(args.out.resolve())]
    if args.check_dir:
        command.extend(["--check-dir", str(args.check_dir.resolve())])
    env = os.environ.copy()
    env["MINTECH_ARTIFACT_MODULES"] = str(modules.resolve())
    subprocess.run(command, check=True, env=env)


if __name__ == "__main__":
    main()
