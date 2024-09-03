import csv
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, send_file
import io

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/plot')
def plot():
    # 쿼리 파라미터 가져오기
    subcategory = request.args.get('subcategory')
    cul_type = request.args.get('cul_type')

    # 첫 번째 CSV 파일 처리
    with open("static/culture_a.csv", "r") as f1:
        data1 = csv.reader(f1)
        header1 = next(data1)

        x_labels1 = []
        y_values1 = []

        for row in data1:
            if row[-1] != '':
                if row[1] == subcategory:
                    for index_header, value in enumerate(header1):
                        if cul_type in value.split():
                            x_labels1.append(value.split()[0])
                            y_values1.append(int(float(row[index_header].replace(',', ''))))  # 소수점 제거

    # 두 번째 CSV 파일 처리
    with open("static/culture_b.csv", "r") as f2:
        data2 = csv.reader(f2)
        header2 = next(data2)

        x_labels2 = []
        y_values2 = []

        for row in data2:
            if row[-1] != '':
                if row[1] == subcategory:
                    for index_header, value in enumerate(header2):
                        if cul_type in value.split():
                            x_labels2.append(value.split()[0])
                            y_values2.append(float(row[index_header].replace('-', '0')))

    # 그래프 그리기
    plt.rc('font', family='Malgun Gothic')
    fig, ax1 = plt.subplots(figsize=(12, 8))  # 크기 조정

    # 첫 번째 y축 (왼쪽)
    ax1.plot(x_labels1, y_values1, marker='o', linestyle='-', color='lightseagreen', label='평균 소비', linewidth=1,
             markersize=4)
    ax1.tick_params(axis='y', labelcolor='lightseagreen')
    ax1.set_xticks(range(len(x_labels1)))
    ax1.set_xticklabels(x_labels1)

    y1_min = min(y_values1) * 0.5
    y1_max = max(y_values1) * 1.2
    ax1.set_ylim(y1_min, y1_max)

    # 두 번째 y축 (오른쪽)
    ax2 = ax1.twinx()  # 공유된 x축을 사용하는 두 번째 y축
    ax2.plot(x_labels2, y_values2, marker='o', linestyle='-', color='darkslategray', label='빈도', linewidth=1,
             markersize=4)
    ax2.tick_params(axis='y', labelcolor='darkslategray')

    y2_min = min(y_values2) * 0.3
    y2_max = max(y_values2) * 1.3
    ax2.set_ylim(y2_min, y2_max)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    if subcategory == "전체":
        plt.title(f"서울시의 연간 {cul_type} 방문 빈도 및 평균 소비", fontsize=20, pad=20)
    else:
        plt.title(f"서울시 {subcategory}의 연간 {cul_type} 방문 빈도 및 평균 소비", fontsize=20, pad=20)

    # 표 데이터 준비
    data = []
    avg_change = []
    freq_change = []

    for i in range(len(x_labels1)):
        if i == 0:
            avg_percent_change = '-'
            freq_percent_change = '-'
        else:
            avg_percent_change = f"{((y_values1[i] - y_values1[i - 1]) / y_values1[i - 1] * 100):.0f}%"
            freq_percent_change = f"{((y_values2[i] - y_values2[i - 1]) / y_values2[i - 1] * 100):.2f}%"

        data.append([x_labels1[i], y_values1[i], y_values2[i], avg_percent_change, freq_percent_change])

    # 표 추가
    table = plt.table(cellText=data,
                      colLabels=['날짜', '평균 소비', '빈도', '평균 소비 증감률', '빈도 증감률'],
                      cellLoc='center',
                      loc='bottom',
                      bbox=[0.0, -0.6, 1.0, 0.5])  # 표를 더 크게 조정

    table.auto_set_font_size(False)
    table.set_fontsize(12)  # 폰트 크기를 키움
    table.auto_set_column_width([0, 1, 2, 3, 4])

    for key, cell in table.get_celld().items():
        cell.set_text_props(fontsize=12, fontstyle='normal')  # 글씨 크기 조정

    fig.tight_layout()

    # 이미지 저장
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)  # 버퍼의 처음으로 이동

    # 이미지 URL을 제공하기 위해
    img_url = "/image?plot=True"

    return render_template('plot.html', img_url=img_url)


@app.route('/image')
def image():
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')


if __name__ == "__main__":
    app.run(host='192.168.15.220', port=5000, debug=True)
