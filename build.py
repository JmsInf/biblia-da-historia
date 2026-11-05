# Gera os pacotes Windows e Linux a partir dos zips do Electron em cache
# (o electron-packager trava silenciosamente no Node 24, então montamos manualmente).
# Uso: npm install  (baixa/cacheia o Electron)  ->  python build.py
import glob, json, os, shutil, tarfile, zipfile, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
ver = json.load(open("node_modules/electron/package.json", encoding="utf-8"))["version"]
APPNAME = "Biblia da Historia"
cache = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~/.cache")), "electron", "Cache")

def find_zip(plat):
    hits = glob.glob(os.path.join(cache, "**", f"electron-v{ver}-{plat}-x64.zip"), recursive=True)
    if hits: return hits[0]
    # baixa se faltar
    subprocess.run(["npx", "@electron/get", "--help"], capture_output=True)
    sys.exit(f"Zip do Electron {ver} para {plat} não encontrado no cache: {cache}")

shutil.rmtree("dist", ignore_errors=True)
os.makedirs("dist")

def make(plat, exe_from, exe_to):
    out = os.path.join("dist", f"{APPNAME}-{plat}-x64")
    with zipfile.ZipFile(find_zip(plat)) as z: z.extractall(out)
    os.rename(os.path.join(out, exe_from), os.path.join(out, exe_to))
    app = os.path.join(out, "resources", "app")
    os.makedirs(app)
    shutil.copytree("app", os.path.join(app, "app"))
    for f in ("main.js", "preload.js", "package.json"): shutil.copy(f, app)
    return out

# Windows -> .zip
w = make("win32", "electron.exe", f"{APPNAME}.exe")
with zipfile.ZipFile(w + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    for r, _, fs in os.walk(w):
        for f in fs:
            fp = os.path.join(r, f); z.write(fp, os.path.join(os.path.basename(w), os.path.relpath(fp, w)))

# Linux -> .tar.gz com permissão de execução
l = make("linux", "electron", "biblia-da-historia")
def fix(ti):
    if ti.isdir(): ti.mode = 0o755
    elif ti.isfile():
        b = os.path.basename(ti.name)
        ti.mode = 0o755 if b in ("biblia-da-historia", "chrome_crashpad_handler", "chrome-sandbox") or b.endswith(".so") or ".so." in b else 0o644
    return ti
with tarfile.open(l + ".tar.gz", "w:gz") as t:
    t.add(l, arcname=os.path.basename(l), filter=fix)
print("OK:", *sorted(os.listdir("dist")), sep="\n  ")
