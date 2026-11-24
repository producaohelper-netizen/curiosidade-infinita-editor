"""Render MP4s through the official Concat MCP server (headless)."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
import time


class Concat:
    def __init__(self, binary, root):
        env = os.environ.copy()
        for key in ("CONCAT_API_ADDRESS", "CONCAT_API_TOKEN"):
            env.pop(key, None)
        env["CONCAT_MCP_ROOTS"] = str(root)
        self.process = subprocess.Popen(
            [binary, "--mcp", "headless"], env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            text=True, encoding="utf-8", bufsize=1,
        )
        self.lines = queue.Queue()
        self.request_id = 0
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        try:
            for line in self.process.stdout:
                self.lines.put(json.loads(line))
        except Exception as exc:
            self.lines.put(exc)
        finally:
            self.lines.put(None)

    def send(self, message):
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", **message}) + "\n")
        self.process.stdin.flush()

    def request(self, method, params, timeout=120):
        self.request_id += 1
        self.send({"id": self.request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(method)
            try:
                reply = self.lines.get(timeout=remaining)
            except queue.Empty:
                raise TimeoutError(method) from None
            if reply is None:
                raise RuntimeError("Concat encerrou antes de responder")
            if isinstance(reply, Exception):
                raise reply
            if reply.get("id") != self.request_id:
                continue
            if "error" in reply:
                raise RuntimeError(f"{method}: {reply['error']}")
            return reply["result"]

    def initialize(self):
        self.request("initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "curiosidade-infinita", "version": "1"},
        })
        self.send({"method": "notifications/initialized"})
        version = self.tool("concat_version")
        if version.get("mcp", {}).get("mode") != "headless":
            raise RuntimeError("Concat não está em modo headless")
        print("Concat MCP headless conectado.", flush=True)

    def tool(self, name, **args):
        result = self.request("tools/call", {"name": name, "arguments": args})
        if result.get("isError"):
            raise RuntimeError(f"{name}: {result.get('content')}")
        return result.get("structuredContent") or {}

    def close(self):
        try:
            self.process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.process.stdout.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--video", required=True, type=Path)
    p.add_argument("--output", default=Path("output/concat-final.mp4"), type=Path)
    p.add_argument("--title", default="")
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=1920)
    p.add_argument("--binary", default="concat")
    args = p.parse_args()
    root = Path.cwd().resolve()
    video, output = args.video.resolve(), args.output.resolve()
    if not video.is_relative_to(root) or not output.is_relative_to(root):
        p.error("Use arquivos dentro do repositório.")
    if not video.is_file() or video.suffix.lower() != ".mp4":
        p.error("MP4 de entrada não encontrado.")
    if output.suffix.lower() != ".mp4" or output == video or output.exists():
        p.error("A saída deve ser um novo MP4, diferente da entrada.")
    if min(args.width, args.height) < 16 or any(v % 2 for v in (args.width, args.height)):
        p.error("Dimensões positivas e pares são necessárias.")
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="concat-", dir=root) as work:
        mcp = Concat(args.binary, root)
        try:
            mcp.initialize()
            name = "Short"
            project = str(Path(work) / name)
            mcp.tool("project_create", location=work, name=name,
                     video={"width": args.width, "height": args.height,
                            "rateNum": 30, "rateDen": 1})
            imported = mcp.tool("media_import", path=project, file=str(video))
            media_id = imported["createdId"]
            timeline = mcp.tool("clips_add_sequence", path=project,
                                mediaIds=[media_id], start=0)["timeline"]
            duration = timeline["duration"]
            if duration <= 0:
                raise RuntimeError("Timeline vazia.")
            if args.title.strip():
                mcp.tool("title_add", path=project, start=0,
                         duration=min(3.0, duration), above=True,
                         style={"content": args.title.strip()})
            mcp.tool("project_save", path=project)
            job = mcp.tool("export_start", path=project, output=str(output),
                           codec="h264", preset="fast")["job"]
            deadline = time.monotonic() + 900
            while True:
                status = mcp.tool("export_wait", job=job, timeoutSeconds=30)
                print("Concat:", status.get("state"), status.get("stage"), flush=True)
                if status.get("state") == "done":
                    break
                if status.get("state") != "running":
                    raise RuntimeError(f"Falha na exportação: {status}")
                if time.monotonic() > deadline:
                    mcp.tool("export_cancel", job=job)
                    raise TimeoutError("Exportação excedeu 15 minutos.")
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError("Concat não gerou o MP4.")
            mcp.tool("project_close", path=project, save=True)
        finally:
            mcp.close()
    print(f"MP4 exportado: {output}", flush=True)


if __name__ == "__main__":
    main()
