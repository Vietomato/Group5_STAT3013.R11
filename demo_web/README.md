# Web demo Olist chạy trên máy

Web dùng dữ liệu và mô hình thật trong repo, phục vụ video demo 15 phút. Giao diện bằng tiếng Anh để khớp lời thuyết minh; hướng dẫn ở đây bằng tiếng Việt. Web chạy tại localhost, không cần tài khoản, dịch vụ ngoài hoặc kết nối Internet khi demo.

## Mở web

Mở Terminal tại thư mục `PTTK`, chạy:

```powershell
.\.venv-boosting\Scripts\python.exe demo_web/server.py
```

Chờ hai dòng `Problem 1 model: ready; frozen hashes verified` và `Problem 2 model: ready; frozen hash verified`, sau đó mở **http://127.0.0.1:8501** bằng Chrome hoặc Edge. Giữ Terminal đang chạy trong lúc demo. Nhấn `Ctrl+C` để dừng.

Cũng có thể chạy launcher, nếu PowerShell cho phép chạy script:

```powershell
.\demo_web\run_demo.ps1
```

Nếu cổng đang được dùng, chọn cổng khác:

```powershell
.\.venv-boosting\Scripts\python.exe demo_web/server.py --port 8502
```

Mở `http://127.0.0.1:8502` tương ứng. Có thể chạy `server.py` từ thư mục khác vì các đường dẫn dữ liệu được tính từ vị trí file.

## Hai bài toán trong web

| Trang | Câu hỏi | Dữ liệu | Mô hình | Kết quả đã chốt |
|---|---|---|---|---|
| **1 · Will it be late?** | Đơn có trễ không? | Mọi đơn có nhãn; mẫu demo lấy từ Test | CatBoost phân loại + hiệu chỉnh sigmoid + ngưỡng 5,418% | Test: recall 94,25%, precision 6,42% |
| **2 · How many days?** | Nếu trễ thì trễ bao nhiêu ngày? | Chỉ đơn trễ; mẫu demo lấy từ Validation A+B, không dùng Test | `CatBoostDelayRegressor` (MAE), so với baseline luôn đoán 7 ngày | MAE 4,53 so với 4,41 ngày; không tốt hơn baseline |

Hai mô hình dùng cùng 21 biến lúc đặt hàng. Kết quả Bài toán 1 hiện thêm dòng "nếu trễ, ước lượng X ngày" từ Bài toán 2, kèm lưu ý ước lượng này không chính xác hơn baseline. Bảng Mock orders 2026 có thêm cột `If late · days`.

## Demo các phần như thế nào

### Problem 2 · How many days?

1. Chọn **Late order D01–D08**, bấm **Load sample**. Tám đơn trễ thật của Validation A+B, hai đơn cho mỗi nhóm trễ 1–3, 4–7, 8–14 và trên 14 ngày; trong mỗi nhóm có một đơn CatBoost đoán sát hơn và một đơn baseline sát hơn. Menu không tiết lộ số ngày trễ.
2. Bấm **Estimate days late**: server gọi `predict` thật của `CatBoostDelayRegressor`, nâng kết quả dưới 1 ngày lên 1, và hiện cạnh baseline 7 ngày.
3. Bấm **Reveal actual delay** để xem số ngày trễ thật và mỗi cách đoán lệch bao nhiêu. Một đơn chỉ để minh họa; kết luận dựa vào MAE trên 567 đơn.
4. Sửa đầu vào (ví dụ khoảng cách) và chạy lại để thấy độ nhạy của mô hình. Đây không phải tác động nhân quả.
5. Phía dưới trang là bằng chứng đã lưu: bảng MAE, khoảng tin cậy, sai số theo nhóm trễ, kiểm tra chia Train theo thời gian, việc thời tiết đóng vai "dấu vân tay ngày", và mức dùng biến. Nguồn: `outputs/tables/delay_prediction/regression_catboost/` và `regression_train_diagnostics/`.

Mô hình Bài toán 2 cần file `outputs/models/delay_regression/CatBoostDelayRegressor.joblib` (tạo bởi `notebooks/06_delay_prediction/02_delay_regression_catboost.ipynb`). Server kiểm tra SHA-256 với `experiment_log.json` trước khi nạp; nếu thiếu, trang vẫn hiện kết quả đã lưu nhưng khóa nút dự đoán.

### Dashboard

- Hiện tổng đơn, số nhãn hợp lệ, số đơn trễ và tỷ lệ trễ. Mẫu đầy đủ phải hiện 99.441 đơn, 96.470 nhãn hợp lệ, 6.534 đơn trễ, tỷ lệ 6,77%.
- Chọn **Destination state** hoặc **Purchase month**: các chỉ số và biểu đồ được tính lại trên cohort đã lọc, không thay đổi dữ liệu nguồn.
- Di chuột vào điểm/cột để xem tỷ lệ cùng số đơn. Nhóm ít hơn 30 đơn được tô xám; không xếp hạng mức rủi ro chỉ từ tỷ lệ của nhóm quá ít đơn.
- **Reset filters** trở về toàn bộ dữ liệu. Bộ lọc chỉ áp dụng cho Dashboard.

### Statistical insights

- Chọn **Distance / Freight / Holiday / Rainfall** để đọc phương pháp, cỡ mẫu, ước lượng, CI và p-value đã hiệu chỉnh Holm; đối chiếu với OR hồi quy.
- Chỉ đường OR = 1 khi giải thích khoảng tin cậy. Với mưa, nói rõ kết quả giảm sau kiểm soát thời kỳ mua hàng.
- Chuyển **Validation A / Test** để thấy CatBoost được chọn trên A, trong khi Random Forest có AP cao nhất trên Test. Không đổi mô hình theo thứ hạng Test.
- Chỉ 6.922 false alerts trong ma trận nhầm lẫn; giải thích recall 94,25% đi cùng precision 6,42% và alert rate 78,32%.
- Đây là các kết quả nghiên cứu đã lưu, không phải chạy lại hồi quy/kiểm định khi bấm chọn. Nhãn trên màn hình ghi rõ phạm vi này.

### Problem 1 · Will it be late?

1. Chọn **Sample 01**, bấm **Load sample** nếu vừa đổi lựa chọn. Web nạp đủ 21 biến từ một đơn Test thật, chưa hiện kết quả thực tế.
2. Đọc các trường chính. Mở **Calendar, products & weather** để thấy 14 biến còn lại. Các biến không sửa vẫn giữ giá trị của đơn đã nạp; không phải mô hình chỉ cần bảy trường chính.
3. Bấm **Run prediction**. Server thực sự gọi `predict_proba` của pipeline CatBoost, rồi bộ hiệu chỉnh sigmoid đã lưu. Không lấy xác suất lưu sẵn để giả lập dự báo.
4. Đọc xác suất đã hiệu chỉnh, ngưỡng khoảng 5,418% và nhãn cảnh báo. Xác suất thô cũng được hiện để đối chiếu.
5. Bấm **Reveal actual outcome** để hiện đơn đó thực tế trễ hay không. Mười hai mẫu được chọn gồm cả dự báo đúng, cảnh báo sai và bỏ sót. Các mẫu được chọn để minh họa, không đại diện cho hiệu năng chung.
6. Đổi một đầu vào, ví dụ khoảng cách. Web đánh dấu kết quả cũ đã lỗi thời. Bấm **Run prediction** lần nữa: so sánh xác suất mới với xác suất đơn gốc đã chạy ở bước 3. Mức thay đổi có thể tăng, giảm hoặc bằng không tùy đầu vào.
7. Nói đây là phản ứng của mô hình khi thay dữ liệu, không phải hiệu quả can thiệp có quan hệ nhân quả. Đầu vào giả định có thể không phản ánh một đơn hàng khả thi ngoài thực tế.
8. Kết quả thực tế không được dùng để đối chiếu với tình huống đã sửa. Bấm **Restore sample** và chạy lại để quay về đơn gốc.
9. Có thể bấm **Download result** để tải JSON gồm đầu vào và dự báo hiện tại. Web không ghi đè dữ liệu, mô hình hoặc các bảng kết quả nghiên cứu.

Để thể hiện giới hạn rõ hơn khi quay: Sample 01 là ví dụ cảnh báo đúng; Sample 04 là cảnh báo sai; Sample 07 là bỏ sót; Sample 10 là không cảnh báo đúng. Thứ tự này dựa vào kết quả Test đã lưu, không phải chọn mẫu ngẫu nhiên. Menu không tiết lộ sẵn kết quả cho người xem.

## Thử đơn giả lập năm 2026

Có hai bộ đơn tự tạo, mỗi đơn đủ 21 biến:

| Bộ | Mã | Ngày mua | Dùng để |
|---|---|---|---|
| Order book | `MOCK-2026-001` … `012` | 26/11 – 25/12/2026 | Bảng Mock orders 2026, có kịch bản Giáng sinh và ngày lễ |
| Try-out | `TRY-2026-01` … `10` | 28/11 – 07/12/2026, mỗi ngày 1 đơn | Chọn thẳng trong menu mẫu của **cả hai bài toán** để chạy thử ngay |

Mười đơn Try-out được thiết kế để thấy dự đoán thay đổi: đơn nội thành hẹn giao ngắn, mưa lớn nơi nhận, tuyến rất xa nhưng hẹn ngắn, hẹn giao 30 ngày, ba người bán, hàng cồng kềnh giá cao, vùng xa phía bắc có mưa, đơn rạng sáng, mưa nơi gửi, đơn nhiều món về Đông Bắc.

Trong trang Problem 1 hoặc Problem 2, mở menu mẫu, chọn nhóm **2026 try-out**, bấm **Load sample** rồi chạy. Nút xem kết quả thực tế bị khóa vì đơn giả lập không có kết quả.

Trang **Mock orders 2026** hiện cả 22 đơn, cột Set phân biệt hai bộ. Bấm **Predict all orders** để chạy CatBoost và bộ hiệu chỉnh thật trên toàn bộ lô; cột Probability, Alert và If late · days được điền sau khi mô hình chạy. Không có cột thực tế, precision, recall hay accuracy vì bộ mock không có nhãn kết quả.

- **Order book CSV** và **Try-out CSV** tải dữ liệu giả lập; file nằm tại `demo_web/data/mock_orders_2026.csv` và `demo_web/data/try_orders_2026.csv`.
- **Download predictions** tải đầu vào kèm xác suất thô, xác suất đã hiệu chỉnh, cảnh báo và ngưỡng.
- **Inspect** mở một đơn trong trang Problem 1. Có thể sửa đầu vào, chạy lại và so sánh với lần dự báo đơn gốc. Nút Reveal actual outcome bị vô hiệu hóa cho mọi đơn mock.
- Dashboard và kết quả thống kê vẫn dùng dữ liệu lịch sử, không ghép các đơn mock vào dữ liệu nghiên cứu.

Giá, khoảng cách, thông tin sản phẩm và thời tiết đều là giả lập; không phải dữ liệu giao dịch hay quan trắc thật năm 2026. Các biến giờ, thứ, số ngày giao dự kiến và ngày dự kiến được tính từ timestamp. Lịch ngày lễ giả định chỉ gồm 25/12/2026 và 01/01/2027 cho các cửa sổ của bộ mock này, không phải lịch ngày lễ quốc gia đã xác minh. Số ngày tới lễ tính cả hôm nay; số lễ trong cửa sổ dùng `(ngày mua, ngày dự kiến]` theo quy ước của project.

Mô hình giữ nguyên từ dữ liệu 2016–2018, chưa được đánh giá trên dữ liệu thật năm 2026. Năm tuyệt đối không nằm trong 21 biến, nên đổi ngày sang năm 2026 không tự cập nhật mô hình theo điều kiện kinh doanh năm 2026. Kết quả dùng minh họa luồng suy luận, không phải bằng chứng về độ chính xác cho năm 2026.

Có thể tái tạo fixture và xuất dự báo mà không mở trình duyệt:

```powershell
.\.venv-boosting\Scripts\python.exe demo_web/generate_mock_orders.py
.\.venv-boosting\Scripts\python.exe demo_web/predict_mock_orders.py
```

Lệnh đầu ghi lại cả hai bộ cố định (bộ 12 đơn cũ không đổi). Lệnh sau ghi `demo_web/data/mock_orders_2026_predictions.csv`; không huấn luyện lại hoặc sửa mô hình. Khi cập nhật code lúc server đang chạy, dừng server bằng `Ctrl+C`, chạy lại rồi nhấn `Ctrl+F5` trên trình duyệt.

## Khung quay 15 phút với web

| Thời gian | Thao tác |
|---|---|
| 00:00–02:00 | Giới thiệu bài toán, nhãn và dashboard toàn bộ mẫu |
| 02:00–04:00 | Lọc bang/tháng, đọc biểu đồ và giải thích mất cân bằng |
| 04:00–07:00 | Statistical insights: kiểm định và hồi quy, phân biệt liên hệ với nhân quả |
| 07:00–09:00 | Timeline chia tập, Validation A/Test và ma trận nhầm lẫn |
| 09:00–12:00 | Problem 1: nạp mẫu, chạy, mở outcome, sửa đầu vào, chạy lại |
| 12:00–13:00 | Problem 2: chạy một đơn trễ, mở số ngày thực tế, đọc kết luận không hơn baseline |
| 13:00–15:00 | Mở code `server.py` ở hàm `predict` nếu cần chứng minh luồng chạy; kết luận và hạn chế |

Kịch bản đọc tiếng Anh cũ nằm ở [kịch bản demo](../docs/demo/kich_ban_demo_15_phut.md). Thứ tự chuyển màn hình của bản cũ dành cho notebook; dùng bảng trên khi quay web. Không đọc những câu hướng dẫn chuyển sang notebook nếu đang trình bày web.

## Môi trường và mô hình

Không thêm thư viện web: backend dùng HTTP server chuẩn của Python, frontend dùng HTML/CSS/JavaScript và SVG. Các thư viện dự báo có sẵn trong môi trường nghiên cứu: NumPy, pandas, joblib, scikit-learn và CatBoost. Cần dùng môi trường tương thích với mô hình; repo ghi nhận Python 3.14.6 và phiên bản tại `requirements.txt`.

Các đầu vào bắt buộc trên ổ đĩa:

- Dataset `data/processed/research_data_weather_price_holiday_assume_utc.csv`.
- Danh sách biến `docs/predictor_list.csv`.
- Các CSV kết quả trong `outputs/tables/` và `data/ml_preparation/split_summary.csv`.
- Cấu hình `outputs/tables/machine_learning/ml_calibration/final_config.json`.
- Pipeline `outputs/models/ml_selection/CatBoostBaseline.joblib`.
- Bộ hiệu chỉnh `outputs/models/ml_calibration/sigmoid_calibrator.joblib`.

Server kiểm tra SHA-256 của pipeline và bộ hiệu chỉnh theo cấu hình trước khi nạp. Đầu vào được sắp đúng thứ tự 21 biến. Giá trị thiếu đi qua preprocessing đã fit trên Train. Xác suất thô được clip bằng epsilon trong cấu hình, đổi sang log-odds, rồi qua calibrator. Ngưỡng được đọc từ cấu hình, không chỉnh bằng giao diện hoặc chọn lại trên Test.

Model binaries đang bị Git bỏ qua theo thiết kế của repo. Khi chuyển máy hoặc clone mới, cần tự tái tạo artifacts theo thứ tự notebook trong README gốc. Nếu thiếu/sai hash model, web vẫn cho xem dashboard và kết quả thống kê nhưng vô hiệu hóa nút dự báo; không sinh dự báo giả để thay thế.

Ứng dụng chỉ bind `127.0.0.1`, phù hợp quay demo trên máy. Đây không phải cấu hình triển khai công khai.

## Kiểm tra

```powershell
.\.venv-boosting\Scripts\python.exe -m unittest discover -s demo_web -p "test_*.py" -v
```

Các kiểm tra đối chiếu dự báo với kết quả Test đã lưu, kiểm tra bộ lọc, giá trị thiếu, dữ liệu nhập không hợp lệ và API HTTP. Chạy kiểm tra không huấn luyện lại mô hình và không ghi đè kết quả nghiên cứu.
