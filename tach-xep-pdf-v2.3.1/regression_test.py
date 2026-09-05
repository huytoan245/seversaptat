from pathlib import Path

def detached(face_count, ltr=True):
    total=face_count*2
    out=[]
    for i in range(face_count):
        left=(i,'L'); right=(i,'R')
        first,second=(left,right) if ltr else (right,left)
        if i%2==0:
            out.append((total-i,first)); out.append((i+1,second))
        else:
            out.append((i+1,first)); out.append((total-i,second))
    return [x for _,x in sorted(out)]

def expected_60_ltr():
    exp=[]
    for page in range(1,61):
        if page<=30:
            face=page-1
            side='R' if face%2==0 else 'L'
        else:
            face=60-page
            side='L' if face%2==0 else 'R'
        exp.append((face,side))
    return exp

x=detached(30,True)
assert x==expected_60_ltr(), (x[:8], expected_60_ltr()[:8])
assert len(set(x))==60
x2=detached(30,False)
assert len(x2)==60 and len(set(x2))==60

src=Path(__file__).with_name('TachXepTrangPDF.cs').read_text(encoding='utf-8')
required=[
    'File đang xử lý:',
    'TỰ XOAY THÔNG MINH',
    'RestoreListFocus',
    'SourceRotation',
    'OriginalSourceIndex',
    'CutPercent = 50.0',
    'OnnxOrientationAnalyzer',
    'Microsoft.ML.OnnxRuntime',
    'ProcessCmdKey',
    'NativeMethods.SetFocus',
    'HorizontalLineScore',
    'File.Replace',
    'Backups',
    'TỰ CHIA & SẮP XẾP',
]
for s in required:
    assert s in src, s
print('REGRESSION_LOGIC_OK')
