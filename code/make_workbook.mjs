// Carrier seating and witness-coupon workbook. QA fixtures are never exported.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import assert from 'node:assert/strict';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
function option(key, fallback) {
  const index = args.indexOf(key);
  return index < 0 ? fallback : args[index + 1];
}
const out = option('--out', path.join(project, 'workbooks/carrier_coupon_comparison.xlsx'));
const checkDir = option('--check-dir', null);
const modules = process.env.MINTECH_ARTIFACT_MODULES;
if (!modules) throw new Error('Run python code/make_workbook.py to select the Artifact Tool runtime.');
const resolveArtifact = createRequire(path.join(modules, '..', 'artifact-resolver.cjs'));
const { Workbook, SpreadsheetFile } = await import(pathToFileURL(resolveArtifact.resolve('@oai/artifact-tool')).href);

const wb = Workbook.create();
const sheetNames = ['00_안내', '01_기록시트', '02_쌍체비교', '03_증거요약', '04_참고기준', '05_입력예시', '06_문헌벤치마크'];
const [guide, log, pairs, evidence, rules, example, literature] = sheetNames.map(name => wb.worksheets.add(name));
const navy = '#17365D';
const blue = '#D9EAF7';
const yellow = '#FFF2CC';
const pale = '#E9EFF6';
const green = '#E2F0D9';
const red = '#FCE4D6';

function cell(sheet, address, value) { sheet.getRange(address).values = [[value]]; }
function formula(sheet, address, value) { sheet.getRange(address).formulas = [[value]]; }
function base(sheet, range, widths) {
  sheet.showGridLines = false;
  sheet.getRange(range).format.font = { name: 'Arial', size: 10, color: '#172B4D' };
  sheet.getRange(range).format.verticalAlignment = 'center';
  sheet.getRange(range).format.rowHeight = 22;
  widths.forEach((width, index) => { sheet.getRangeByIndexes(0, index, 1, 1).format.columnWidth = width; });
}
function title(sheet, text, endColumn) {
  sheet.mergeCells(`A1:${endColumn}1`);
  cell(sheet, 'A1', text);
  sheet.getRange(`A1:${endColumn}1`).format = {
    fill: navy,
    font: { name: 'Arial', size: 15, bold: true, color: '#FFFFFF' },
    rowHeight: 32,
  };
}
function header(sheet, row, labels) {
  const range = sheet.getRangeByIndexes(row - 1, 0, 1, labels.length);
  range.values = [labels];
  range.format = {
    fill: navy,
    font: { name: 'Arial', size: 9, bold: true, color: '#FFFFFF' },
    wrapText: true,
    horizontalAlignment: 'center',
    rowHeight: 44,
  };
}
function inputRange(sheet, address) {
  sheet.getRange(address).format.fill = yellow;
  sheet.getRange(address).format.font.color = '#0000CC';
}
function note(sheet, address, text, fill = '#FFFFFF') {
  sheet.mergeCells(address);
  cell(sheet, address.split(':')[0], text);
  sheet.getRange(address).format.wrapText = true;
  sheet.getRange(address).format.fill = fill;
}
function twoColumn(sheet, row, label, text) {
  cell(sheet, `A${row}`, label);
  cell(sheet, `B${row}`, text);
  sheet.getRange(`A${row}`).format.font.bold = true;
  sheet.getRange(`A${row}`).format.fill = pale;
  sheet.getRange(`B${row}`).format.wrapText = true;
  sheet.getRange(`A${row}:B${row}`).format.rowHeight = 46;
}
function numberValidation(sheet, address, minimum = 0) {
  sheet.getRange(address).dataValidation = { rule: { type: 'decimal', operator: 'greaterThanOrEqual', formula1: String(minimum) } };
}
function wholeValidation(sheet, address, minimum = 0) {
  sheet.getRange(address).dataValidation = { rule: { type: 'whole', operator: 'greaterThanOrEqual', formula1: String(minimum) } };
}

base(guide, 'A1:B20', [27, 110]);
title(guide, 'Mintech 캐리어 안착 및 Witness Coupon 비교분석', 'B');
for (const [row, label, text] of [
  [3, '목적', '방법 A/B에서 캐리어 안착, 시편 준비, witness coupon 배치와 고정 측정점 두께 범위를 함께 비교한다.'],
  [4, '실측 원칙', '노란 셀에 확인한 값만 입력한다. 실제 관찰 입력 영역은 비어 있으며, 미측정값을 0 또는 정상으로 채우지 않는다.'],
  [5, '소프트웨어 검증', '별도 코드와 12번 보고서에서 SOFTWARE_TEST 입력의 누락·중복·조건 불일치를 검사한다. 시험 데이터는 이 워크북의 실측 영역에 넣지 않는다.'],
  [6, '01_기록시트', '개별 실행의 식별자, 안착·핀·표면 확인, coupon 좌표·방향, 준비 오류·재작업, recipe, 측정 도구·지점·두께를 기록한다.'],
  [7, '02_쌍체비교', '같은 block과 pair에서 방법 A/B의 고정 측정점 두께 범위(nm)와 네 가지 오류 건수를 한 행에 입력한다.'],
  [8, '유효 쌍', 'pair_id가 고유하고 실행 순서가 1/2로 서로 다르며 모든 수치가 0 이상이고 evidence_status가 FIELD_MEASUREMENT인 행만 집계한다.'],
  [9, '연속 결과', '고정 측정점 두께 범위(nm)를 A/B 쌍체차로 계산한다. delta = A - B이며 양수면 B의 범위가 더 작다.'],
  [10, '이산 결과', '캐리어 안착 오류, 준비 오류, coupon 위치 오류, coupon 방향 오류를 방법별 합계와 쌍당 평균으로 요약한다.'],
  [12, 'FIELD_MEASUREMENT', '현장에서 직접 측정하고 원자료를 추적할 수 있는 값. 유효 쌍의 필수 자료 구분이다.'],
  [13, 'RECONSTRUCTED_EXAMPLE', '입력 형식을 설명하려고 재구성한 예시. 05_입력예시에만 있으며 실제 합계와 통계에서 제외한다.'],
  [14, '입력 색상', '노란 배경과 파란 글씨는 사용자 입력, 흰 배경과 검은 글씨는 수식 또는 설명이다.'],
  [15, 'LITERATURE_BENCHMARK', '06_문헌벤치마크의 공개 연구값이다. 현장 측정, 회사 규격, 합격 기준 또는 A/B 계산 입력이 아니다.'],
  [16, '4M 결과', '03_증거요약은 별도의 합성 4M 모델 결과다. 캐리어/coupon 실측 결과와 섞어 해석하지 않는다.'],
  [17, '참고 기준', '04_참고기준에서 유효성, 계산식, 좌표·방향·두께 기록 규칙을 확인한다.'],
  [18, '반복 측정', '같은 쌍과 측정점을 반복 측정하면 같은 pair_id·measurement_point에 별도 record_id로 행을 추가하고 notes에 반복 회차를 적는다.'],
  [19, '제외 실행', '중단하거나 제외한 실행은 행을 지우지 않고 notes에 사유를 적는다. 필수값이 비면 유효 기록·유효 쌍 집계에서 빠진다.'],
]) twoColumn(guide, row, label, text);

const csvPath = path.join(project, 'templates/field_records.csv');
const csvText = (await fs.readFile(csvPath, 'utf8')).replace(/^\uFEFF/, '').trim();
assert.ok(!csvText.includes('\n'), 'The public CSV must contain only its header.');
const csvHeader = csvText.split(',');
assert.deepEqual(csvHeader, [
  'record_id', 'date', 'method', 'run_order', 'block_id', 'pair_id', 'carrier_id',
  'carrier_seating_check', 'carrier_pin_check', 'carrier_surface_check',
  'carrier_seating_error_count', 'preparation_error_count', 'rework_count', 'recipe_id',
  'coupon_id', 'coupon_x_mm', 'coupon_y_mm', 'coupon_orientation_deg',
  'coupon_position_error_count', 'coupon_orientation_error_count', 'measurement_tool',
  'measurement_point', 'thickness_nm', 'measured_by', 'evidence_status', 'notes',
]);
const logHeaders = [...csvHeader, 'record_status'];
const logWidths = [16, 13, 10, 11, 14, 15, 15, 18, 16, 18, 18, 17, 14, 15, 15, 13, 13, 17, 18, 20, 18, 19, 15, 16, 22, 32, 20];
base(log, 'A1:AA112', logWidths);
title(log, '캐리어 및 Witness Coupon 실측 기록시트', 'J');
note(log, 'A2:J2', '실제 관찰 입력용. 한 행은 한 방법 실행과 한 측정점을 나타낸다. 빈칸은 미관찰이며 0으로 간주하지 않는다.', blue);
header(log, 4, logHeaders);
inputRange(log, 'A5:Z104');
log.getRange('AA5:AA104').format.fill = '#FFFFFF';
log.getRange('AA5:AA104').format.font.color = '#172B4D';
log.getRange('B5:B104').setNumberFormat('yyyy-mm-dd');
log.getRange('P5:R104').setNumberFormat('0.000');
log.getRange('W5:W104').setNumberFormat('0.000');
// Guard arithmetic with IF: Excel AND does not short-circuit text operands.
function numericInput(address, integer = false, minimum = 0, upper = null) {
  const rules = [`${address}>=${minimum}`];
  if (integer) rules.push(`MOD(${address},1)=0`);
  if (upper !== null) rules.push(`${address}<${upper}`);
  return `IF(ISNUMBER(${address}),AND(${rules.join(',')}),FALSE)`;
}
for (let row = 5; row <= 104; row++) {
  const missing = Array.from({length: 25}, (_, i) => `ISBLANK(${String.fromCharCode(65 + i)}${row})`);
  const rules = [
    numericInput(`B${row}`, true, 1),
    `OR(C${row}="A",C${row}="B")`, `OR(D${row}=1,D${row}=2)`,
    ...['H', 'I', 'J'].map(c => `OR(${c}${row}="PASS",${c}${row}="FAIL")`),
    ...['K', 'L', 'M', 'S', 'T'].map(c => numericInput(`${c}${row}`, true)),
    ...['P', 'Q', 'W'].map(c => numericInput(`${c}${row}`)),
    numericInput(`R${row}`, false, 0, 360), `Y${row}="FIELD_MEASUREMENT"`,
  ];
  formula(log, `AA${row}`, `=IF(COUNTA(A${row}:Z${row})=0,"",IF(OR(${missing.join(',')}),"필수값 입력",IF(COUNTIFS($A$5:$A$104,A${row})>1,"중복 ID",IF(AND(${rules.join(',')}),"유효 기록","입력 확인"))))`);
}
for (const column of ['C']) log.getRange(`${column}5:${column}104`).dataValidation = { rule: { type: 'list', values: ['A', 'B'] } };
log.getRange('D5:D104').dataValidation = { rule: { type: 'list', values: ['1', '2'] } };
for (const column of ['H', 'I', 'J']) log.getRange(`${column}5:${column}104`).dataValidation = { rule: { type: 'list', values: ['PASS', 'FAIL'] } };
log.getRange('Y5:Y104').dataValidation = { rule: { type: 'list', values: ['FIELD_MEASUREMENT'] } };
for (const column of ['K', 'L', 'M', 'S', 'T']) wholeValidation(log, `${column}5:${column}104`);
for (const column of ['P', 'Q', 'R', 'W']) numberValidation(log, `${column}5:${column}104`);
log.tables.add('A4:AA104', true, 'CarrierCouponRecords');
log.freezePanes.freezeRows(4);
log.freezePanes.freezeColumns(2);
header(log, 107, ['기록 요약', '값']);
cell(log, 'A108', '유효 FIELD 기록'); formula(log, 'B108', '=COUNTIFS(AA5:AA104,"유효 기록")');
cell(log, 'A109', '입력 확인 필요'); formula(log, 'B109', '=COUNTIFS(AA5:AA104,"필수값 입력")+COUNTIFS(AA5:AA104,"중복 ID")+COUNTIFS(AA5:AA104,"입력 확인")');
note(log, 'A111:J111', '이 시트의 입력은 02_쌍체비교에 자동 전송되지 않는다. 원자료 추적용 기록이며 쌍체 입력은 검토 후 별도로 작성한다.', pale);

const pairHeaders = [
  'pair_id', 'block_id', 'A_order', 'A_carrier_id', 'A_coupon_id', 'A_thickness_range_nm',
  'A_carrier_seating_errors', 'A_preparation_errors', 'A_coupon_position_errors', 'A_coupon_orientation_errors',
  'B_order', 'B_carrier_id', 'B_coupon_id', 'B_thickness_range_nm', 'B_carrier_seating_errors',
  'B_preparation_errors', 'B_coupon_position_errors', 'B_coupon_orientation_errors', 'evidence_status', 'notes',
  'pair_status', 'valid_A_nm', 'valid_B_nm', 'delta_nm',
];
const pairWidths = [15, 14, 10, 16, 15, 19, 19, 17, 19, 21, 10, 16, 15, 19, 19, 17, 19, 21, 22, 32, 19, 14, 14, 14];
base(pairs, 'A1:X70', pairWidths);
title(pairs, '캐리어 안착 및 Witness Coupon 쌍체 A/B 비교', 'J');
note(pairs, 'A2:J2', '연속 결과는 고정 측정점 두께의 범위(nm)다. 각 방법의 범위는 동일한 측정점 집합에서 max(thickness) - min(thickness)로 산출해 입력한다.', blue);
header(pairs, 4, pairHeaders);
inputRange(pairs, 'A5:T34');
pairs.getRange('U5:X34').format.fill = '#FFFFFF';
pairs.getRange('U5:X34').format.font.color = '#172B4D';
pairs.getRange('F5:F34').setNumberFormat('0.000');
pairs.getRange('N5:N34').setNumberFormat('0.000');
pairs.getRange('V5:X34').setNumberFormat('0.000');
for (let row = 5; row <= 34; row++) {
  const missing = Array.from({length: 18}, (_, i) => `ISBLANK(${String.fromCharCode(66 + i)}${row})`);
  const rules = [
    `OR(AND(C${row}=1,K${row}=2),AND(C${row}=2,K${row}=1))`,
    ...['F', 'N'].map(c => numericInput(`${c}${row}`)),
    ...['G', 'H', 'I', 'J', 'O', 'P', 'Q', 'R'].map(c => numericInput(`${c}${row}`, true)),
    `S${row}="FIELD_MEASUREMENT"`,
  ];
  formula(pairs, `U${row}`, `=IF(COUNTA(A${row}:T${row})=0,"",IF(ISBLANK(A${row}),"pair ID 입력",IF(COUNTIFS($A$5:$A$34,A${row})>1,"중복 ID",IF(OR(${missing.join(',')}),"필수값 입력",IF(AND(${rules.join(',')}),"유효 쌍","입력 확인")))))`);
  formula(pairs, `V${row}`, `=IF(U${row}="유효 쌍",F${row},"")`);
  formula(pairs, `W${row}`, `=IF(U${row}="유효 쌍",N${row},"")`);
  formula(pairs, `X${row}`, `=IF(U${row}="유효 쌍",V${row}-W${row},"")`);
}
for (const column of ['C', 'K']) pairs.getRange(`${column}5:${column}34`).dataValidation = { rule: { type: 'list', values: ['1', '2'] } };
pairs.getRange('S5:S34').dataValidation = { rule: { type: 'list', values: ['FIELD_MEASUREMENT'] } };
for (const column of ['F', 'N']) numberValidation(pairs, `${column}5:${column}34`);
for (const column of ['G', 'H', 'I', 'J', 'O', 'P', 'Q', 'R']) wholeValidation(pairs, `${column}5:${column}34`);
pairs.tables.add('A4:X34', true, 'CarrierCouponPairs');
pairs.freezePanes.freezeRows(4);
pairs.freezePanes.freezeColumns(2);

header(pairs, 38, ['연속 결과', '방법 A', '방법 B', '쌍체차 A-B', '정의']);
pairs.getRange('E38:E52').format.columnWidth = 48;
for (const [row, label, definition] of [
  [39, '유효 쌍 수', '고유 ID, 반대 실행 순서, 비음수 수치, FIELD_MEASUREMENT를 모두 만족한 쌍'],
  [40, '평균 두께 범위(nm)', '동일한 고정 측정점 집합의 max - min'],
  [41, '표준편차(nm)', '방법별 범위와 쌍체차의 표본 표준편차'],
  [42, '표준오차(nm)', 'SD(delta) / sqrt(n)'],
  [43, '쌍체 t', '평균(delta) / 표준오차'],
  [44, '자유도', 'n - 1'],
  [45, '양측 p값', '두 방법의 평균 범위 차이가 0이라는 귀무가설'],
  [46, '효과크기 dz', '평균(delta) / SD(delta)'],
  [47, '95% CI 하한(nm)', '평균(delta)의 양측 신뢰구간'],
  [48, '95% CI 상한(nm)', '차이 분포, 이상치, 쌍의 독립성을 함께 검토'],
  [49, '입력 확인 행', '미완성, 중복, 순서 오류, 음수 또는 자료 구분 오류'],
  [50, '계산 상태', '2쌍 미만 또는 delta 분산 0이면 추론통계를 표시하지 않음'],
]) { cell(pairs, `A${row}`, label); cell(pairs, `E${row}`, definition); pairs.getRange(`E${row}`).format.wrapText = true; }
formula(pairs, 'D39', '=COUNT(X5:X34)'); formula(pairs, 'B39', '=D39'); formula(pairs, 'C39', '=D39');
for (const [column, source] of [['B', 'V'], ['C', 'W'], ['D', 'X']]) {
  formula(pairs, `${column}40`, `=IF(D39=0,"",AVERAGE(${source}5:${source}34))`);
  formula(pairs, `${column}41`, `=IF(D39<2,"",STDEV(${source}5:${source}34))`);
}
formula(pairs, 'D42', '=IF(D39<2,"",D41/SQRT(D39))');
formula(pairs, 'D43', '=IF(OR(D39<2,D41=0),"",D40/D42)');
formula(pairs, 'D44', '=IF(D39<2,"",D39-1)');
formula(pairs, 'D45', '=IF(OR(D39<2,D41=0),"",TDIST(ABS(D43),D44,2))');
formula(pairs, 'D46', '=IF(OR(D39<2,D41=0),"",D40/D41)');
formula(pairs, 'D47', '=IF(OR(D39<2,D41=0),"",D40-_xlfn.T.INV(0.975,D44)*D42)');
formula(pairs, 'D48', '=IF(OR(D39<2,D41=0),"",D40+_xlfn.T.INV(0.975,D44)*D42)');
formula(pairs, 'D49', '=COUNTIFS(U5:U34,"pair ID 입력")+COUNTIFS(U5:U34,"중복 ID")+COUNTIFS(U5:U34,"필수값 입력")+COUNTIFS(U5:U34,"입력 확인")');
formula(pairs, 'D50', '=IF(D39=0,"측정값 입력 전",IF(D39<2,"유효 쌍 추가 입력",IF(D41=0,"차이 분산 0: 검정 제외","쌍체 통계 계산됨")))');
pairs.getRange('B40:D48').setNumberFormat('0.000');
pairs.getRange('D44').setNumberFormat('0');
pairs.getRange('D45').setNumberFormat('0.0000');
pairs.getRange('A50:E50').format.rowHeight = 34;

header(pairs, 54, ['이산 오류 요약', '방법 A 합계', '방법 B 합계', 'A 쌍당 평균', 'B 쌍당 평균']);
const discrete = [
  [55, '캐리어 안착 오류', 'G', 'O'],
  [56, '준비 오류', 'H', 'P'],
  [57, 'Coupon 위치 오류', 'I', 'Q'],
  [58, 'Coupon 방향 오류', 'J', 'R'],
];
for (const [row, label, aColumn, bColumn] of discrete) {
  cell(pairs, `A${row}`, label);
  formula(pairs, `B${row}`, `=IF($D$39=0,"",SUMIFS(${aColumn}$5:${aColumn}$34,$U$5:$U$34,"유효 쌍"))`);
  formula(pairs, `C${row}`, `=IF($D$39=0,"",SUMIFS(${bColumn}$5:${bColumn}$34,$U$5:$U$34,"유효 쌍"))`);
  formula(pairs, `D${row}`, `=IF($D$39=0,"",B${row}/$D$39)`);
  formula(pairs, `E${row}`, `=IF($D$39=0,"",C${row}/$D$39)`);
}
pairs.getRange('B55:C58').setNumberFormat('0');
pairs.getRange('D55:E58').setNumberFormat('0.00');
note(pairs, 'A61:J61', '오류 건수는 관찰한 발생 건수다. 확인하지 않은 항목은 0이 아니라 빈칸으로 두며, 해당 행은 유효 쌍에서 제외된다.', pale);

const metadata = JSON.parse(await fs.readFile(path.join(project, 'outputs', 'run_metadata.json'), 'utf8'));
const modelSource = path.join(project, 'outputs', 'results.csv');
const csvWb = await Workbook.fromCSV(await fs.readFile(modelSource, 'utf8'), { sheetName: 'ResultsSource' });
const metrics = csvWb.worksheets.getItem('ResultsSource').getUsedRange().values;
assert.deepEqual(metrics[0], ['model', 'roc_auc', 'pr_auc', 'f1_defect', 'tn', 'fp', 'fn', 'tp']);
base(evidence, 'A1:J20', [29, 13, 13, 13, 9, 9, 9, 9, 14, 14]);
title(evidence, '별도 4M 합성 모델 결과', 'J');
note(evidence, 'A3:J3', `합성 ${metadata.n.toLocaleString()}행, seed ${metadata.seed}, 생성 양성 ${metadata.positive_rows}행, 임계값 ${metadata.threshold}. 캐리어/coupon 현장 측정과 별도 자료.`, blue);
header(evidence, 5, ['모델', 'ROC-AUC', 'AP', 'F1', 'TN', 'FP', 'FN', 'TP', '재현율', '정밀도']);
for (let index = 1; index < metrics.length; index++) {
  const row = 5 + index;
  evidence.getRange(`A${row}:H${row}`).values = [[metrics[index][0], ...metrics[index].slice(1).map(Number)]];
  formula(evidence, `I${row}`, `=H${row}/(G${row}+H${row})`);
  formula(evidence, `J${row}`, `=H${row}/(F${row}+H${row})`);
}
evidence.getRange('B6:D7').setNumberFormat('0.0000');
evidence.getRange('E6:H7').setNumberFormat('0');
evidence.getRange('I6:J7').setNumberFormat('0.0%');
for (const [row, text, fill] of [
  [10, '범위: 별도로 생성한 4M 품질 분류 예제다. 이 워크북의 캐리어 안착 또는 witness coupon A/B 결과가 아니다.', '#FFFFFF'],
  [12, '해석: 합성 데이터의 모델 비교 결과이며 회사 실측 성능, 개선율 또는 배포 효과로 해석하지 않는다.', '#FFFFFF'],
  [14, '표시 출처: outputs/results.csv(지표), outputs/4m_quality_analysis_data.csv(입력 데이터), outputs/run_metadata.json(seed·분할·패키지 버전). AP는 pr_auc 열의 average precision 값이다.', pale],
  [16, '연결 경계: 01_기록시트와 02_쌍체비교의 FIELD_MEASUREMENT 입력은 이 모델 결과에 자동 연결되지 않는다.', '#FFFFFF'],
  [18, 'FN은 생성 라벨 1을 임계값 0.5 미만으로, FP는 생성 라벨 0을 임계값 이상으로 분류한 건수다. 체크리스트 오류나 회사 생산 결함의 누락·오경보가 아니다. class_weight="balanced"를 쓰므로 0.5를 실제 결함 확률이나 운영 최적 임계값으로 해석하지 않는다.', '#FFFFFF'],
]) { note(evidence, `A${row}:J${row + 1}`, text, fill); }

base(rules, 'A1:B21', [29, 108]);
title(rules, '캐리어 및 Witness Coupon 기록·계산 기준', 'B');
for (const [row, label, text] of [
  [3, '쌍체 단위', '같은 block에서 비교 가능한 carrier/coupon 조건으로 수행한 방법 A와 B를 하나의 pair_id로 묶는다. pair_id는 입력표에서 고유해야 한다.'],
  [4, '실행 순서', 'A_order와 B_order는 각각 1 또는 2이며 서로 달라야 한다. AB와 BA 순서를 block에 배분해 순서 효과를 확인한다.'],
  [5, '자료 구분', '유효 쌍은 FIELD_MEASUREMENT만 허용한다. RECONSTRUCTED_EXAMPLE은 05_입력예시에만 둔다.'],
  [6, '문헌 벤치마크', 'LITERATURE_BENCHMARK는 출처별 비교 맥락이며 현장 합계, A/B 통계, 모델 증거와 연결하지 않는다.'],
  [7, '캐리어 확인', '안착, 핀, 표면 상태를 실행 전에 확인한다. 오류 건수와 PASS/FAIL 확인 결과를 원자료에 함께 남긴다.'],
  [8, 'Coupon 위치', '현재 입력은 x/y >= 0, 방향 0도 이상 360도 미만이다. 현장 원점과 좌표계가 다르면 입력 기준과 수식을 먼저 바꾼다.'],
  [9, '준비와 재작업', '준비 오류와 재작업 횟수를 분리한다. 관찰하지 않은 오류는 0으로 기록하지 않고 빈칸으로 둔다.'],
  [10, 'Recipe와 도구', 'recipe ID, 측정 도구, 측정 지점 이름을 기록한다. 교정 상태와 측정 절차는 해당 원자료에서 추적한다.'],
  [12, '두께 범위', '각 방법에서 동일한 고정 측정점 집합의 두께를 nm로 측정하고 range = max(thickness_nm) - min(thickness_nm)로 계산한다.'],
  [13, '쌍체차', 'delta_nm = A_thickness_range_nm - B_thickness_range_nm. 양수면 방법 B의 고정점 두께 범위가 더 작다.'],
  [14, '수치 유효성', '두께 범위와 모든 오류 건수는 숫자이며 0 이상이어야 한다. 오류 건수는 정수여야 하고, 소수점이 있으면 입력 확인으로 처리한다. 필수 오류 건수가 비면 해당 쌍을 집계하지 않는다.'],
  [15, '추론통계', '2쌍 이상이며 SD(delta) > 0일 때 t, 양측 p값, dz와 95% 신뢰구간을 계산한다. 차이 분포와 이상치를 별도로 검토한다.'],
  [17, '이산 요약', '유효 쌍만 대상으로 캐리어 안착, 준비, coupon 위치, coupon 방향 오류의 방법별 합계와 쌍당 평균을 계산한다.'],
  [18, '빈 입력', '실측 전 입력 영역은 비어 있어야 한다. 0은 확인 결과가 실제로 0건일 때만 입력한다.'],
  [20, '4M 출력 출처', '별도 표시 파일: outputs/4m_quality_analysis_data.csv. 평가 지표: outputs/results.csv. 합성 생성 메타데이터와 패키지 버전: outputs/run_metadata.json.'],
]) twoColumn(rules, row, label, text);

base(example, 'A1:T10', pairWidths.slice(0, 20));
title(example, '입력 예시 - 실제 집계 제외', 'H');
note(example, 'A2:H2', '아래 한 행은 형식 설명용 RECONSTRUCTED_EXAMPLE이다. 02_쌍체비교의 표·수식·합계와 연결되지 않는다.', red);
header(example, 4, pairHeaders.slice(0, 20));
example.getRange('A5:T5').values = [[
  'EXAMPLE-001', 'BLOCK-01', 1, 'CAR-A01', 'CP-A01', 12.4, 0, 1, 0, 0,
  2, 'CAR-B01', 'CP-B01', 9.8, 0, 0, 1, 0, 'RECONSTRUCTED_EXAMPLE', '입력 형식 설명용이며 실측값이 아님',
]];
example.getRange('A5:T5').format.fill = red;
example.getRange('A5:T5').format.font.color = '#9C0006';
example.getRange('A5:T5').format.wrapText = true;
example.getRange('A5:T5').format.rowHeight = 40;
example.getRange('S5').format.columnWidth = 30;
example.getRange('T5').format.columnWidth = 34;
example.getRange('F5:F5').setNumberFormat('0.000');
example.getRange('N5:N5').setNumberFormat('0.000');
note(example, 'A7:H8', '예시의 두께 범위와 오류 건수는 설명을 위해 재구성한 값이다. 이 행을 실제 입력표로 복사하지 말고, 원자료에서 확인한 값만 새 pair_id로 입력한다.', pale);
example.freezePanes.freezeRows(4);

const literatureHeaders = [
  'Data_Class', '재료·적층 구조', '기판', '증착 맥락', '물성', '값', '단위', '측정 기준', '출처', 'URL/DOI',
];
const parkContext = 'dual-target DC magnetron sputtering, 실온 성장, 기판 약 50 °C, AZO 타깃 20 W';
const jeongContext = 'linear facing-target sputtering, 실온, 기판 가열·도펀트 활성화 없음';
const yunContext = 'IZO sputtering 후 polymer solution coating, sputtering 중 약 100 °C 가열';
const leeAzoContext = 'in-line magnetron sputtering, 실온 증착, 열처리 단계 보고 없음; AZO 2 kW pulsed DC, 200 kHz, 0.5 µs, 5 mTorr, 50 sccm Ar';
const leeAgContext = `${leeAzoContext}; Ag 60 W RF, 3 mTorr, 30 sccm Ar, 실온`;
const literatureRows = [
  ['AZO 혼합 ITO, 150 nm', '미기재', parkContext, '비저항', 4.6e-4, 'Ω·cm', '', 'Park et al. (2008), publisher abstract', 'https://doi.org/10.1149/1.2976160'],
  ['AZO 혼합 ITO, 150 nm', '미기재', parkContext, '투과율', 85, '%', '550 nm', 'Park et al. (2008), publisher abstract', 'https://doi.org/10.1149/1.2976160'],
  ['AZO 혼합 ITO, 150 nm', '미기재', parkContext, 'FoM', 9.83e-3, 'Ω^-1', '원문 표기 유지', 'Park et al. (2008), publisher abstract', 'https://doi.org/10.1149/1.2976160'],
  ['AZO 혼합 ITO, 150 nm', '미기재', parkContext, '일함수', 5.2, 'eV', '', 'Park et al. (2008), publisher abstract', 'https://doi.org/10.1149/1.2976160'],
  ['AZO, 막 두께 미기재', 'PET', jeongContext, '면저항', 39, 'Ω/□', '', 'Jeong et al. (2010), publisher abstract', 'https://doi.org/10.1088/0022-3727/43/46/465403'],
  ['AZO, 막 두께 미기재', 'PET', jeongContext, '투과율', 84.86, '%', '가시광 평균', 'Jeong et al. (2010), publisher abstract', 'https://doi.org/10.1088/0022-3727/43/46/465403'],
  ['AgNW / IZO / PEDOT:PSS, 초록의 전기·광학 값', 'PEN', yunContext, '면저항', 5.9, 'Ω/□', '특정 IZO 두께와 일괄 대응하지 않음', 'Yun et al. (2016), abstract', 'https://doi.org/10.1038/srep34150'],
  ['AgNW / IZO / PEDOT:PSS, 초록의 전기·광학 값', 'PEN', yunContext, '투과율', 86, '%', '550 nm, 특정 두께와 일괄 대응하지 않음', 'Yun et al. (2016), abstract', 'https://doi.org/10.1038/srep34150'],
  ['AgNW / IZO / PEDOT:PSS, 본문의 AFM 시편', 'PEN', yunContext, 'RMS 거칠기', 4.3, 'nm', 'Fig. 4 및 본문', 'Yun et al. (2016), full text', 'https://doi.org/10.1038/srep34150'],
  ['AgNW / IZO / PEDOT:PSS, 본문의 AFM 시편', 'PEN', yunContext, 'peak-to-valley 거칠기', 33.5, 'nm', 'Fig. 4 및 본문', 'Yun et al. (2016), full text', 'https://doi.org/10.1038/srep34150'],
  ['32/0/32 nm AZO/Ag/AZO', 'glass', `${leeAzoContext}; Ag 조건 해당 없음`, '면저항', 717.03, 'Ω/□', '', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/0/32 nm AZO/Ag/AZO', 'glass', `${leeAzoContext}; Ag 조건 해당 없음`, '투과율', 82.77, '%', '550 nm', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/0/32 nm AZO/Ag/AZO', 'glass', `${leeAzoContext}; Ag 조건 해당 없음`, 'FoM', 0.21, 'mΩ^-1', '원문 표기 유지', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/6/32 nm AZO/Ag/AZO', 'glass', leeAgContext, '면저항', 64.17, 'Ω/□', '', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/6/32 nm AZO/Ag/AZO', 'glass', leeAgContext, '투과율', 77.06, '%', '550 nm', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/6/32 nm AZO/Ag/AZO', 'glass', leeAgContext, 'FoM', 1.15, 'mΩ^-1', '원문 표기 유지', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/12/32 nm AZO/Ag/AZO', 'glass', leeAgContext, '면저항', 12.22, 'Ω/□', '', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/12/32 nm AZO/Ag/AZO', 'glass', leeAgContext, '투과율', 76.62, '%', '550 nm', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
  ['32/12/32 nm AZO/Ag/AZO', 'glass', leeAgContext, 'FoM', 4.65, 'mΩ^-1', '원문 표기 유지', 'Lee et al. (2024), Micromachines 15(1), 146', 'https://doi.org/10.3390/mi15010146'],
].map(row => ['LITERATURE_BENCHMARK', ...row]);

base(literature, 'A1:J29', [23, 38, 20, 64, 25, 14, 14, 20, 34, 42]);
title(literature, 'OLED 박막 문헌 벤치마크 - 현장 계산 제외', 'J');
note(literature, 'A2:J2', '공개 연구의 비교 맥락만 수록한다. Mintech 현장 측정·회사 규격·합격 기준이 아니며 01_기록시트, 02_쌍체비교, 요약 수식, 03_증거요약과 연결되지 않는다.', '#E4DFEC');
header(literature, 4, literatureHeaders);
literature.getRange('A4:J4').format.fill = '#5B3F78';
literature.getRange(`A5:J${4 + literatureRows.length}`).values = literatureRows;
literature.getRange(`A5:J${4 + literatureRows.length}`).format.fill = '#F3EFF8';
literature.getRange(`A5:J${4 + literatureRows.length}`).format.font.color = '#2F2040';
literature.getRange(`A5:J${4 + literatureRows.length}`).format.wrapText = true;
literature.getRange(`A5:J${4 + literatureRows.length}`).format.rowHeight = 58;
literature.getRange(`F5:F${4 + literatureRows.length}`).setNumberFormat('0.#####');
literature.tables.add(`A4:J${4 + literatureRows.length}`, true, 'LiteratureBenchmarks');
note(literature, 'A25:J25', 'Yun의 초록 값과 본문 AFM 값은 특정 한 두께 시편의 묶음으로 해석하지 않는다. Kim과 Choi는 이번 검토에서 원문을 대조하지 못해 수치표에서 제외했다. FoM은 연구 간에 합치지 않는다.', '#E4DFEC');
literature.getRange('A25:J25').format.rowHeight = 42;
literature.freezePanes.freezeRows(4);
literature.freezePanes.freezeColumns(2);

const checks = [];
function close(actual, expected, label, tolerance = 1e-8) {
  assert.ok(typeof actual === 'number' && Math.abs(actual - expected) < tolerance, `${label}: ${actual} != ${expected}`);
  checks.push(label);
}
function value(sheet, address) { return sheet.getRange(address).values[0][0]; }
function blank(actual, label) {
  assert.ok(actual === '' || actual === null || actual === undefined, `${label}: ${actual}`);
  checks.push(label);
}
function equals(actual, expected, label) { assert.equal(actual, expected, label); checks.push(label); }

if (checkDir) {
  await fs.mkdir(checkDir, { recursive: true });
  close(value(pairs, 'D39'), 0, 'blank real pair table has zero valid pairs');
  close(value(log, 'B108'), 0, 'blank real record table has zero valid records');
  equals(literatureRows.length, 19, 'rechecked literature property rows retained');
  equals(literatureRows.every(row => row[0] === 'LITERATURE_BENCHMARK'), true, 'all benchmark rows have literature category');
  close(value(log, 'B108'), 0, 'benchmark rows do not affect field record totals');
  close(value(pairs, 'D39'), 0, 'benchmark rows do not affect valid pair totals');
  blank(value(pairs, 'D45'), 'blank real pair table has no p-value');
  equals(value(example, 'S5'), 'RECONSTRUCTED_EXAMPLE', 'example is explicitly reconstructed');
  close(value(pairs, 'D39'), 0, 'example sheet is excluded from real totals');

  const field = 'FIELD_MEASUREMENT';
  pairs.getRange('A5:T7').values = [
    ['QA-1', 'B1', 1, 'CA1', 'CPA1', 12, 0, 1, 0, 0, 2, 'CB1', 'CPB1', 10, 0, 0, 1, 0, field, 'QA fixture'],
    ['QA-2', 'B1', 2, 'CA2', 'CPA2', 15, 1, 0, 0, 1, 1, 'CB2', 'CPB2', 12, 0, 1, 0, 0, field, 'QA fixture'],
    ['QA-3', 'B2', 1, 'CA3', 'CPA3', 18, 0, 0, 1, 0, 2, 'CB3', 'CPB3', 14, 1, 0, 0, 1, field, 'QA fixture'],
  ];
  close(value(pairs, 'D39'), 3, 'valid paired rows accepted');
  close(value(pairs, 'D40'), 3, 'paired mean thickness-range difference');
  close(value(pairs, 'D41'), 1, 'paired thickness-range standard deviation');
  close(value(pairs, 'D42'), 1 / Math.sqrt(3), 'standard error agrees with independent arithmetic');
  close(value(pairs, 'D43'), 3 * Math.sqrt(3), 'paired t agrees with independent arithmetic');
  close(value(pairs, 'D45'), 1 - Math.sqrt(27 / 29), 'two-sided df=2 t probability agrees with closed form', 1e-6);
  close(value(pairs, 'D47'), 3 - 4.302652729911275 / Math.sqrt(3), '95 percent lower confidence bound', 1e-6);
  close(value(pairs, 'D48'), 3 + 4.302652729911275 / Math.sqrt(3), '95 percent upper confidence bound', 1e-6);
  close(value(pairs, 'B55'), 1, 'carrier seating errors summarized for A');
  close(value(pairs, 'C57'), 1, 'coupon position errors summarized for B');

  cell(pairs, 'F5', -1);
  close(value(pairs, 'D39'), 2, 'negative thickness range excluded');
  cell(pairs, 'F5', 12);
  cell(pairs, 'G5', -1);
  close(value(pairs, 'D39'), 2, 'negative error count excluded');
  cell(pairs, 'G5', 0);
  cell(pairs, 'G5', 0.5);
  close(value(pairs, 'D39'), 2, 'fractional error count excluded');
  cell(pairs, 'G5', 0);
  pairs.getRange('H5').clear({ applyTo: 'contents' });
  close(value(pairs, 'D39'), 2, 'missing error count excluded');
  cell(pairs, 'H5', 1);
  cell(pairs, 'G5', 'zero');
  equals(value(pairs, 'U5'), '입력 확인', 'text error count has readable status instead of formula error');
  close(value(pairs, 'D49'), 1, 'text count remains visible in invalid pair summary');
  cell(pairs, 'G5', 0);
  cell(pairs, 'A7', 'QA-2');
  close(value(pairs, 'D39'), 1, 'duplicate pair IDs excluded');
  cell(pairs, 'A7', 'QA-3');
  cell(pairs, 'K5', 1);
  close(value(pairs, 'D39'), 2, 'invalid A/B order excluded');
  cell(pairs, 'K5', 2);
  cell(pairs, 'S5', 'SOFTWARE_TEST');
  close(value(pairs, 'D39'), 2, 'software tests excluded from field pair totals');
  cell(pairs, 'S5', 'LITERATURE_BENCHMARK');
  close(value(pairs, 'D39'), 2, 'literature input excluded from field pair totals');
  cell(pairs, 'S5', field);

  cell(pairs, 'N5', 10); cell(pairs, 'N6', 13); cell(pairs, 'N7', 16);
  close(value(pairs, 'D41'), 0, 'zero delta variance detected');
  blank(value(pairs, 'D45'), 'zero variance suppresses p-value');

  pairs.getRange('A5:T34').clear({ applyTo: 'contents' });
  close(value(pairs, 'D39'), 0, 'all pair fixtures removed');
  close(value(pairs, 'D49'), 0, 'blank pair input has no invalid rows');
  log.getRange('A5:Y5').values = [[
    'QA-REC-1', 45000, 'A', 1, 'B1', 'QA-1', 'CA1', 'PASS', 'PASS', 'PASS',
    0, 0, 0, 'RCP-1', 'CP-A1', 0, 0, 0, 0, 0, 'TOOL-1', 'P1', 100, 'QA', field,
  ]];
  close(value(log, 'B108'), 1, 'observed zero error counts are valid');
  cell(log, 'R5', 360);
  close(value(log, 'B108'), 0, 'angle at 360 is rejected');
  cell(log, 'R5', 359.5);
  close(value(log, 'B108'), 1, 'angle just below 360 is accepted');
  cell(log, 'R5', 0);
  cell(log, 'B5', 'invalid-date');
  close(value(log, 'B108'), 0, 'text date rejected');
  equals(value(log, 'AA5'), '입력 확인', 'text date has readable status instead of formula error');
  close(value(log, 'B109'), 1, 'text date remains visible in invalid record summary');
  cell(log, 'B5', 0);
  close(value(log, 'B108'), 0, 'zero date serial rejected');
  cell(log, 'B5', 45000);
  cell(log, 'K5', 'zero');
  equals(value(log, 'AA5'), '입력 확인', 'text record count has readable status');
  close(value(log, 'B109'), 1, 'text record count remains visible in summary');
  cell(log, 'K5', 0);
  cell(log, 'K5', 0.5);
  close(value(log, 'B108'), 0, 'fractional record error count excluded');
  cell(log, 'K5', 0);
  log.getRange('A5:Y5').clear({ applyTo: 'contents' });
  close(value(log, 'B108'), 0, 'real observation area remains blank');
  blank(value(log, 'AA54'), 'middle blank record remains blank');
  blank(value(log, 'AA104'), 'last blank record remains blank');
  blank(value(pairs, 'U34'), 'last blank pair remains blank');
}

wb.recalculate();
const errorScan = await wb.inspect({
  kind: 'match',
  searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 30 },
  maxChars: 2500,
});
console.log('formula_scan', errorScan.ndjson);
assert.ok(!/#(?:REF!|DIV\/0!|VALUE!|NAME\?|N\/A|NUM!|NULL!|SPILL!|CALC!)/.test(errorScan.ndjson), 'Unexpected formula error');

if (checkDir) {
  const renders = [
    ['00_안내', 'A1:B20', 'guide'],
    ['01_기록시트', 'A1:J11', 'record_input'],
    ['01_기록시트', 'U1:AA11', 'record_status'],
    ['02_쌍체비교', 'A1:J12', 'pair_input_a'],
    ['02_쌍체비교', 'K1:X12', 'pair_input_b'],
    ['02_쌍체비교', 'A38:E58', 'pair_summaries'],
    ['03_증거요약', 'A1:J20', 'evidence'],
    ['04_참고기준', 'A1:B20', 'rules'],
    ['05_입력예시', 'A1:T8', 'example'],
    ['06_문헌벤치마크', `A1:J${4 + literatureRows.length + 2}`, 'literature_benchmark'],
  ];
  for (const [sheetName, range, name] of renders) {
    const image = await wb.render({ sheetName, range, scale: 1.25, format: 'png' });
    await fs.writeFile(path.join(checkDir, `${name}.png`), new Uint8Array(await image.arrayBuffer()));
  }
  await fs.writeFile(path.join(checkDir, 'workbook_checks.json'), JSON.stringify({
    checks,
    formulaScan: errorScan.ndjson,
    fixturesRemoved: true,
    publicCsvHeaderOnly: true,
    exampleExcludedFromRealTotals: true,
    benchmarkRows: literatureRows.length,
    benchmarkExcludedFromRealTotals: true,
  }, null, 2));
}

await fs.mkdir(path.dirname(out), { recursive: true });
const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(out);
console.log(`saved: ${out}; ${checks.length} fixture assertions`);
