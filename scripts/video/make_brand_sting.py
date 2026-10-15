"""ブランドの1秒動画（縦・サイトと同じ黒地＋方眼＋アクセント色）。使い方: python3 make_brand_sting.py <出力mp4> <最後のコマpng>"""
import subprocess, tempfile, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,T=1080,1920,30,1.0
BG=(5,5,12);TEXT=(226,232,240);ACC=(0,255,209);MUT=(124,138,160);GRID=(20,21,30);FRAME=(44,46,56)
B="/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc";M="/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
FL=ImageFont.truetype(B,64);FH=ImageFont.truetype(B,92);FS=ImageFont.truetype(M,40);FT=ImageFont.truetype("/System/Library/Fonts/Menlo.ttc",34)
base=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(base)
for x in range(0,W,72): d.line((x,0,x,H),fill=GRID)
for y in range(0,H,72): d.line((0,y,W,y),fill=GRID)
d.rectangle((60,560,W-60,1420),outline=FRAME,width=2)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def frame(t):
    im=base.copy(); L=Image.new("RGBA",(W,H)); dd=ImageDraw.Draw(L)
    dd.text((120,650),"SEADICE",font=FL,fill=ACC)
    dd.text((W-120,668),"ADS 0  REGISTER 0",font=FT,fill=MUT,anchor="ra")
    k1=ease(t/0.25); k2=ease((t-0.12)/0.25)
    def txt(xy,s,f,c,k,dy):
        layer=Image.new("RGBA",(W,H)); ImageDraw.Draw(layer).text((xy[0],xy[1]+round((1-k)*24)),s,font=f,fill=c+(round(255*k),)); L.alpha_composite(layer)
    txt((120,930),"誠実なサービスで、",FH,TEXT,k1,0)
    txt((120,1050),"信頼に応える。",FH,ACC,k2,0)
    txt((120,1230),"研究ベースで、AI時代の問題を",FS,MUT,k2,0)
    txt((120,1290),"解決するサービスを提供中。",FS,MUT,k2,0)
    im.paste(L,(0,0),L); return im
with tempfile.TemporaryDirectory() as tmp:
    for i in range(round(T*FPS)): frame(i/FPS).save(f"{tmp}/{i:03d}.png")
    subprocess.run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",f"{tmp}/%03d.png","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",sys.argv[1]],check=True)
frame(0.9).save(sys.argv[2])
