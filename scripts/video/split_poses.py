"""キャラクターシート（2列3行・背景の市松模様が描き込まれた画像でも可）を6体に切り分け、透明PNGにする。
使い方: python3 split_poses.py <シート.png> <出力フォルダ> [名前1 名前2 ...]（左上から右へ。既定は bow search book point wave think）"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
src, out = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(src).convert("RGB")).astype(int)
H, W, _ = a.shape
sat = a.max(2) - a.min(2); val = a.max(2)
bgish = (sat < 20) & (val > 140)               # 市松模様（灰と白）
lab, n = nd.label(bgish)
border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
bg = np.isin(lab, list(border))
fg = ~bg
fg = nd.binary_opening(fg, iterations=1)       # 市松の取り残しの点を消す
alpha = (fg * 255).astype(np.uint8)
rgba = np.dstack([a.astype(np.uint8), alpha])
names = sys.argv[3:] or ["bow", "search", "book", "point", "wave", "think"]
cw, ch = W // 2, H // 3
for i, name in enumerate(names):
    r, c = divmod(i, 2)
    cell = rgba[r*ch:(r+1)*ch, c*cw:(c+1)*cw].copy()
    m = cell[..., 3] > 0
    l2, k = nd.label(m)
    if k:
        sizes = nd.sum(m, l2, range(1, k+1))
        keep = [j+1 for j, s in enumerate(sizes) if s >= 40]   # 小さなゴミは捨て、飾りは残す
        cell[..., 3] = np.where(np.isin(l2, keep), 255, 0)
    im = Image.fromarray(cell); im = im.crop(im.getbbox())
    im.save(f"{out}/{name}.png"); print(name, im.size)
