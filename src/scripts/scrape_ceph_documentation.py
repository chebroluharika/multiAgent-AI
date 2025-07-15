import io
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

save_dir = Path(__file__).parent.parent.parent / "data/git-clone"
print("Saving to", save_dir)

branch_name = "squid"
response = requests.get(
    f"https://github.com/ceph/ceph/archive/refs/heads/{branch_name}.zip"
)
with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
    zip_ref.extractall(save_dir)

docs_dir = save_dir / f"ceph-{branch_name}/doc"


doc_text = ""
for file in tqdm(docs_dir.glob("**/*.rst")):
    doc_text += file.read_text(encoding="utf-8")

    doc_text += (
        "\n\n-------------------------------------------------------------- \n\n"
    )


save_file = save_dir / "ceph_documentation.txt"
print("Saving to", save_file)

with open(save_file, "w", encoding="utf-8") as f:
    f.write(doc_text)

env_file = save_dir.parent.parent / ".env"
with open(env_file, "a", encoding="utf-8") as env:
    if "DOCUMENTATION" not in env_file.read_text():
        print("Adding DOCUMENTATION path to .env")
        env.write(f"DOCUMENTATION={save_file}\n")

print("Done")
