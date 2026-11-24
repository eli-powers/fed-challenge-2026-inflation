"""Regression test (R1-F01): the slide 3B workbook builder must run on a Q4-2026 SPF with the documented one rerun.

Builds a SYNTHETIC Q4-2026 SPF fixture (made-up medians, never used for any reported number) in a scratch copy of the
pipeline, runs forecast.py --spf 2026Q4, then runs build_slide3b_workbook.py --spf=2026Q4 against that copy. The builder's
semantic_check() asserts that every live-formula scenario cell and gap equals the pipeline's processed grid (1e-5 pp), so a
pass means: gap quarters start at 2026Q4, 2026Q4 is adjusted, and the workbook reproduces the pipeline. Nothing in the real
pipeline, raw folders or 01_Finals is touched.

Run from the project root:  python3 -I "02_Research/Subtasks/12_slide3b_research/code/test_builder_q4_synthetic.py"
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
PIPE = os.path.join(ROOT, '03_Data', 'pipelines', 'forecast_3b')
BUILDER = os.path.join(ROOT, '02_Research', 'Subtasks', '12_slide3b_research', 'code', 'build_slide3b_workbook.py')
SYNTH = [2026, 4, 2.47, 3.0, 2.8, 2.7, 2.6, 2.5, 3.3, 2.65, 2.2]   # YEAR, QUARTER, COREPCE1-6, A, B, C (synthetic)


def main():
    import openpyxl
    tmp = tempfile.mkdtemp(prefix='s3b_q4test_')
    sp = os.path.join(tmp, 'forecast_3b')
    for d in ('code', 'config'):
        shutil.copytree(os.path.join(PIPE, d), os.path.join(sp, d), ignore=shutil.ignore_patterns('__pycache__'))
    os.makedirs(os.path.join(sp, 'processed'))
    raws = sorted(x for x in os.listdir(os.path.join(PIPE, 'raw')) if x[:2] == '20')
    dst = os.path.join(sp, 'raw', '2099-01-01')
    shutil.copytree(os.path.join(PIPE, 'raw', raws[-1]), dst)
    wb = openpyxl.load_workbook(os.path.join(dst, 'medianLevel.xlsx'))
    ws = wb['COREPCE']
    n = ws.max_row + 1
    for j, v in enumerate(SYNTH, 1):
        ws.cell(n, j, v)
    wb.save(os.path.join(dst, 'medianLevel.xlsx'))
    with open(os.path.join(dst, 'spf-release-dates.txt'), 'a') as f:
        f.write('\n2026 Q4 11/10/26 11/16/26\n')   # synthetic deadline: matched STEO becomes nov26
    env = dict(os.environ, SLIDE3B_PIPE=sp, SLIDE3B_OUT=os.path.join(tmp, 'Slide3B_Q4_SYNTHETIC.xlsx'))
    r1 = subprocess.run([sys.executable, '-I', os.path.join(sp, 'code', 'forecast.py'), '--spf', '2026Q4'], cwd=ROOT, capture_output=True, text=True)
    print('pipeline (synthetic Q4):', 'OK' if r1.returncode == 0 else 'FAIL', r1.stdout[-300:], r1.stderr[-800:])
    r2 = subprocess.run([sys.executable, '-I', BUILDER, '--spf=2026Q4'], cwd=ROOT, env=env, capture_output=True, text=True)
    out = r2.stdout + r2.stderr
    print('builder (synthetic Q4):', 'OK' if r2.returncode == 0 else 'FAIL')
    print('\n'.join(l for l in out.splitlines() if 'Warning' not in l and 'warn(' not in l)[-1500:])
    shutil.rmtree(tmp)
    assert r1.returncode == 0 and r2.returncode == 0, 'synthetic Q4 rerun failed'
    print('PASS: builder reproduces the pipeline grid on a synthetic Q4 SPF (gap starts 2026Q4; 2026Q4 adjusted).')


if __name__ == '__main__':
    main()
