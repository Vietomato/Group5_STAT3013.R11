# Dự đoán sớm rủi ro giao hàng trễ trong thương mại điện tử Brazil

Đồ án sử dụng **Brazilian E-Commerce Public Dataset by Olist**, bổ sung thông tin sản phẩm, ngày lễ và thời tiết INMET để phân tích giao trễ và dự đoán rủi ro tại thời điểm đặt hàng.

Đã hoàn thành preprocessing, EDA, thống kê suy luận, hồi quy giải thích, baseline ML, xử lý mất cân bằng lớp, calibration, chọn ngưỡng và đánh giá Test. Oversampling/undersampling được thực hiện **sau khi đã xem Test** và được trình bày riêng như phân tích khám phá.

## 1. Mục tiêu và phạm vi

- Mô tả giao trễ theo thời gian, địa lý và đặc điểm đơn hàng.
- Kiểm định mối liên hệ, ước lượng kích thước ảnh hưởng và độ bất định.
- So sánh Logistic Regression, Random Forest, LightGBM, XGBoost, CatBoost và DummyClassifier làm mốc tham chiếu.
- Đánh giá xác suất và ngưỡng cảnh báo theo một protocol chung.

Đây là nghiên cứu quan sát trên dữ liệu lịch sử. Kết quả không chứng minh quan hệ nhân quả và chưa xác nhận hiệu quả triển khai thực tế.

## 2. Cấu trúc project

```text
data/
  raw/                         # 9 bảng Olist gốc
  processed/                   # Bảng đã làm sạch và dataset theo đơn hàng
  external/
    holidays/
    inmet/processed/           # Thời tiết đã xử lý
    inmet/raw/                 # ZIP tự bổ sung; không đưa vào Git
  ml_preparation/               # Manifest và thống kê chia tập
docs/
  data_preprocessing/
  eda/
  inferential_statistics/
  explanatory_regression/
  machine_learning/
  predictor_list.csv            # 21 biến đầu vào ML
notebooks/
  01_data_preprocessing/
  02_eda/
  03_inferential_statistics/
  04_explanatory_regression/
  05_machine_learning/
    data_preparation/
    baselines/
    model_selection/
    calibration/
    test_evaluation/
    sampling_experiments/
outputs/
  tables/                       # Bảng theo nhóm phân tích
  figures/
  models/                       # Pipeline/calibrator cục bộ, không đưa vào Git
  migrations/                   # Metadata trước đổi đường dẫn, không đưa vào Git
README.md
requirements.txt
.gitignore
```

Mục lục: [tài liệu](docs/README.md), [notebook](notebooks/README.md), [quy trình ML](notebooks/05_machine_learning/README.md), [bảng kết quả](outputs/tables/README.md).

## 3. Dữ liệu và nhãn mục tiêu

Dataset theo đơn hàng có **99.441 đơn**, một dòng cho mỗi `order_id`. Có **96.470 nhãn hợp lệ**, gồm **6.534 đơn trễ**, tương ứng **6,77%** trong mẫu có nhãn.

Với đơn đủ điều kiện gắn nhãn:

- `is_late = 1`: ngày giao thực tế sau ngày giao dự kiến.
- `is_late = 0`: giao đúng hoặc trước ngày giao dự kiến.
- Nhãn thiếu: không đủ điều kiện; **không chuyển thành 0**.

So sánh theo ngày lịch, kết hợp điều kiện trạng thái và tính hợp lệ của ngày. Xem [từ điển dataset](docs/data_preprocessing/order_dataset_dictionary.md) và [kiểm tra leakage](docs/eda/data_quality_and_leakage_review.md).

| Đầu vào ML | Vị trí |
|---|---|
| Dataset chính | [research_data_weather_price_holiday_assume_utc.csv](data/processed/research_data_weather_price_holiday_assume_utc.csv) |
| 21 predictors | [predictor_list.csv](docs/predictor_list.csv) |
| Phân chia đơn hàng | [split_manifest.csv](data/ml_preparation/split_manifest.csv) |
| Thống kê chia tập | [split_summary.csv](data/ml_preparation/split_summary.csv) |

Predictors thuộc bốn nhóm: thông tin nội bộ, giá/sản phẩm, ngày lễ và thời tiết. Dataset còn chứa biến kết quả sau mua; chỉ dùng danh sách predictors, không lấy toàn bộ cột làm đầu vào.

CSV gốc và processed hiện được Git theo dõi. Giữ nguyên dữ liệu gốc. Nguồn ngày lễ nằm trong cột `source_url`; [tài liệu INMET](docs/data_preprocessing/inmet_weather_preparation_review.md) mô tả nguồn và cách tổng hợp thời tiết.

### Đầu vào còn thiếu nếu dựng lại thời tiết từ đầu

```text
data/external/inmet/raw/2016.zip
data/external/inmet/raw/2017.zip
data/external/inmet/raw/2018.zip
```

Ba ZIP này chưa có trong workspace và không đưa vào Git. Các bảng thời tiết đã xử lý cùng dataset ML hiện có đầy đủ, nên có thể dùng processed và đọc kết quả mà không dựng lại archive.

## 4. Cài đặt môi trường

Môi trường đã kiểm tra: **Windows, CPython 3.14.6**. Những phiên bản Python khác chưa được xác nhận trong lần bàn giao này.

`requirements.txt` ghim các dependency trực tiếp theo môi trường đã chạy thành công; dependency gián tiếp do pip giải quyết. Đây không phải bản khóa toàn bộ dependency gián tiếp. Mỗi run giữ `package_versions.json` riêng; không mặc định các run cũ đều dùng môi trường hiện tại.

Chạy từ thư mục gốc bằng PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m jupyterlab
```

Trong VS Code, dùng extension Python và Jupyter, rồi chọn `.venv\Scripts\python.exe` làm kernel. Gọi trực tiếp Python trong môi trường ảo giúp không phải đổi execution policy để kích hoạt môi trường.

## 5. Quy trình notebook

### Preprocessing và EDA

1. [clean_olist_tables](notebooks/01_data_preprocessing/clean_olist_tables.ipynb): làm sạch bảng nguồn.
2. [build_order_level_dataset](notebooks/01_data_preprocessing/build_order_level_dataset.ipynb): tạo dataset theo đơn hàng và nhãn.
3. [build_temporal_features](notebooks/01_data_preprocessing/build_temporal_features.ipynb): tạo đặc trưng thời gian.
4. Tạo [giá/sản phẩm](notebooks/01_data_preprocessing/build_price_product_features.ipynb), [ngày lễ](notebooks/01_data_preprocessing/build_holiday_features.ipynb), [thời tiết](notebooks/01_data_preprocessing/prepare_inmet_weather.ipynb), rồi [ghép dataset mở rộng](notebooks/01_data_preprocessing/merge_enriched_features.ipynb).
5. [02_eda](notebooks/02_eda/): khám phá giao trễ, mất cân bằng lớp, thời gian, hủy đơn, review và chất lượng dữ liệu.

Không chạy lại preprocessing trên dataset chính một cách tự động: notebook dựng dataset có bước ghi đè `research_data.csv`; notebook temporal mặc định `EXPORT=False` và còn kiểm tra branch `feat/temporal-feature-enhancement` khi bật xuất. Cần rà soát bước xuất trước khi dựng lại để tránh để dataset thiếu đặc trưng thời gian. Phần INMET còn cần ba ZIP nêu trên. Các giới hạn này chưa được sửa trong lần chuẩn bị tài liệu.

### Thống kê và ML

| Bước | Notebook / thư mục | Nội dung |
|---|---|---|
| Chuẩn bị split | [ml_data_preparation](notebooks/05_machine_learning/data_preparation/ml_data_preparation.ipynb) | Manifest dùng chung trước Stage 4 và ML |
| Stage 3 | [test_delivery_risk_associations](notebooks/03_inferential_statistics/test_delivery_risk_associations.ipynb) | 26 kiểm định chính, Holm, kích thước ảnh hưởng và khoảng tin cậy |
| Stage 4 | [explain_late_delivery_logistic](notebooks/04_explanatory_regression/explain_late_delivery_logistic.ipynb) | M0/M4, độ nhạy và diagnostics; mẫu complete-case 56.553 đơn |
| Baseline | [baselines](notebooks/05_machine_learning/baselines/) | 5 họ mô hình và DummyClassifier |
| Lựa chọn | [model_selection](notebooks/05_machine_learning/model_selection/) | CatBoost có trọng số; chọn và đóng băng pipeline trên A |
| Calibration | [calibration_threshold](notebooks/05_machine_learning/calibration/calibration_threshold.ipynb) | Sigmoid và ngưỡng trên B |
| Test | [final_test_evaluation](notebooks/05_machine_learning/test_evaluation/final_test_evaluation.ipynb) | Đánh giá các cấu hình đã đóng băng |
| Bổ sung sau Test | [sampling_experiments](notebooks/05_machine_learning/sampling_experiments/) | Oversampling/undersampling trên 5 mô hình, chỉ chấm A |

ML được viết trực tiếp trong cell `.ipynb`. Notebook tìm thư mục gốc từ vị trí hiện tại. Dùng kernel sạch cho run mới; thứ tự chi tiết nằm trong [README ML](notebooks/05_machine_learning/README.md).

**Test đã được đánh giá.** Notebook Test chặn chạy lại đánh giá hoàn thành với cùng cấu hình. Đọc kết quả đã lưu thay vì dùng Test để chỉnh mô hình/ngưỡng. Notebook lựa chọn, calibration và Test tham chiếu các run cụ thể; chạy lại baseline không tự thay các tham chiếu đã chốt.

## 6. Thiết kế thí nghiệm

Chia theo thời gian mua, giữ cùng ngày mua trong cùng tập, kết hợp khoảng cách 45 ngày và cutoff nhãn sẵn có. Không chia ngẫu nhiên hoặc chia riêng cho từng mô hình.

| Tập | Số đơn | Đơn trễ | Mục đích |
|---|---:|---:|---|
| Train | 57.449 | 3.720 | Fit preprocessing và classifier |
| Validation A | 7.661 | 387 | So sánh và chọn cấu hình |
| Validation B | 3.115 | 180 | Calibration và chọn ngưỡng |
| Test | 9.445 | 504 | Đánh giá cuối cùng |
| **Tổng** | **77.670** | **4.791** | Theo manifest |

18.800 đơn có nhãn hợp lệ bị loại do khoảng cách thời gian hoặc nhãn chưa sẵn có tại cutoff. Không ép tỷ lệ cuối cùng về 70/20/10.

- **Average Precision (AP)** là chỉ số lựa chọn chính, không đồng nhất với PR-AUC tính bằng hình thang.
- ROC-AUC bổ sung khả năng phân biệt; Brier và Log Loss đánh giá xác suất, thấp hơn tốt hơn.
- Imputation, encoding và scaling chỉ học từ Train. Logistic có scaling; CatBoost dùng categorical native; các cây còn lại dùng one-hot.
- CatBoost baseline được chọn trên A; cấu hình có trọng số kém hơn và không được chọn.
- Sigmoid fit trên log-odds xác suất đã clip trên B. Ngưỡng yêu cầu Recall ≥70%, ưu tiên Precision cao nhất rồi tỷ lệ cảnh báo thấp nhất.
- Calibration và ngưỡng cùng dùng B, nên điểm trên B không phải đánh giá độc lập.

Xem [experiment_protocol.md](docs/machine_learning/experiment_protocol.md) để biết cấu hình, quy tắc phá hòa, cutoff và các lần bổ sung phạm vi.

## 7. Kết quả chính

### Xác suất gốc trên Test

Test gồm 9.445 đơn, tỷ lệ trễ 5,34%. Thứ hạng dưới đây không được dùng để chọn lại mô hình.

| Mô hình | AP ↑ | ROC-AUC ↑ | Brier ↓ | Log Loss ↓ |
|---|---:|---:|---:|---:|
| Random Forest | **0,097815** | **0,703794** | **0,049924** | **0,200420** |
| LightGBM | 0,089018 | 0,677041 | 0,050339 | 0,201280 |
| XGBoost | 0,087707 | 0,682035 | 0,050587 | 0,200834 |
| CatBoost — đã chọn trên A | 0,082843 | 0,674094 | 0,050143 | 0,200854 |
| Logistic Regression | 0,081244 | 0,629901 | 0,051185 | 0,206977 |
| CatBoost có trọng số | 0,073914 | 0,624723 | 0,176899 | 0,535125 |
| DummyClassifier | 0,053362 | 0,500000 | 0,050644 | 0,209432 |

Nguồn: [bảng Test](outputs/tables/machine_learning/ml_test/20261111_160038_411032/seven_model_test_comparison.csv).

### CatBoost tại ngưỡng đã chốt trên B

Ngưỡng xác suất sau calibration: **0,054178902872422004**, quy tắc `p >= threshold`.

| Chỉ số Test | Kết quả |
|---|---:|
| Recall | 94,25% — phát hiện 475/504 đơn trễ |
| Precision | 6,42% |
| F1 | 0,120238 |
| Tỷ lệ cảnh báo | 78,32% — 7.397 đơn |
| TP / FP / FN / TN | 475 / 6.922 / 29 / 2.019 |

Calibration cải thiện điểm B nhưng **làm xác suất Test kém hơn**: Brier tăng 0,050143 → 0,057522; Log Loss tăng 0,200854 → 0,227891. Recall cao đi kèm quá nhiều cảnh báo sai, chưa cho thấy hiệu quả vận hành tốt.

Nguồn: [trước/sau calibration](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_calibration_comparison.csv), [chỉ số tại ngưỡng](outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_threshold_metrics.csv).

### Lấy mẫu lại sau Test

Cùng seed 42 và cùng mẫu Train sau resampling được dùng cho 5 mô hình, giữ nguyên tham số baseline. Preprocessing học trên Train gốc, sau đó chỉ resample hàng dùng để fit classifier. Validation A không resample.

- Oversampling: 53.729 đơn mỗi lớp; chỉ Logistic tăng AP nhẹ.
- Undersampling: 3.720 đơn mỗi lớp; chỉ Random Forest tăng AP so với baseline của chính nó.
- Brier và Log Loss xấu hơn baseline ở cả 5 mô hình với cả hai phương pháp.
- Không cấu hình resampling nào vượt AP của CatBoost baseline trên A. Không thay quyết định đã đóng băng hoặc chấm lại B/Test.

Nguồn: [so sánh ba điều kiện lấy mẫu](outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv).

## 8. Artifact và khả năng tái lập

| Artifact | Vị trí |
|---|---|
| Lựa chọn classifier | [selected_config.json](outputs/tables/machine_learning/ml_selection/20261111_154450_762570/selected_config.json) |
| Calibrator và ngưỡng | [final_config.json](outputs/tables/machine_learning/ml_calibration/20261111_154951_108593/final_config.json) |
| Kiểm tra Test | [evaluation_manifest.json](outputs/tables/machine_learning/ml_test/20261111_160038_411032/evaluation_manifest.json) |
| Chỉ mục bảng | [outputs/tables/README.md](outputs/tables/README.md) |

Run ML lưu metrics, dự đoán theo đơn, audit, tham số, phiên bản và hash. Dùng completion record nếu có và kiểm tra đủ artifact cần thiết; một số thư mục chạy dở được giữ để truy vết, không phải kết quả hoàn thành.

`outputs/models/` không đưa vào Git vì có model nhị phân lớn. **Clone repo không tự khôi phục pipeline/calibrator gốc.** Muốn kiểm tra artifact đã đóng băng hoặc áp dụng chúng cho dữ liệu khác, cần bản lưu model đúng phiên bản/SHA256. Metrics và metadata không thay thế model. Huấn luyện lại tạo bộ artifact mới, không tự thay cấu hình đã chốt trong notebook.

`outputs/reruns/` đã được xóa; notebook không phụ thuộc vào thư mục đó. `outputs/migrations/` là bản sao metadata cục bộ khi đổi đường dẫn, không đưa vào Git. Metadata hiện tại đã được cập nhật đường dẫn và chuỗi hash; số liệu/dự đoán không tính lại trong bước di chuyển.

## 9. Giới hạn và việc còn lại

- Dữ liệu lịch sử không phải mẫu ngẫu nhiên của toàn bộ thị trường Brazil.
- Mẫu dự đoán chỉ gồm đơn cuối cùng có nhãn hợp lệ, không bao phủ trực tiếp mọi đơn hủy/chưa hoàn thành.
- Loại đơn do nhãn chưa sẵn có và complete-case regression có thể tạo sai lệch chọn mẫu.
- Múi giờ nguồn, thời điểm công bố thời tiết và khả năng biết một số thông tin lúc mua chưa được xác minh đầy đủ. Thời tiết theo bang không đo tuyến giao hàng cụ thể.
- Không dùng ngày giao thực tế, thời lượng giao thực tế, review hoặc cờ phát sinh sau mua làm predictor.
- A được dùng lặp lại để chọn mô hình; Test từng xuất hiện trong EDA/Stage 3. Phân tích lấy mẫu lại được bổ sung sau khi xem Test.
- Chưa có khoảng tin cậy cho chênh lệch hiệu năng, kiểm định vận hành hoặc ngưỡng được xác nhận theo chi phí nghiệp vụ.

Cần tổng hợp kết luận Stage 3–5, phân tích nhóm cảnh báo sai/bỏ sót và đối chiếu calibration B/Test cho báo cáo. Những phân tích đó mang tính mô tả, không dùng Test hiện tại để chọn lại mô hình/ngưỡng. Tải ZIP INMET và rà soát xuất temporal nếu cần dựng lại preprocessing từ đầu.

## 10. Chuẩn bị commit

Giữ trong Git: notebook, tài liệu, requirements, predictor list, CSV đang được theo dõi, split manifest, bảng kết quả và biểu đồ. Không đưa môi trường ảo, bí mật, cache, model nhị phân, ZIP INMET gốc, nhật ký tạm hoặc bản sao migration cục bộ vào commit.

```powershell
git status --short
git diff --check
git diff --stat
git add -A
git diff --cached --stat
git diff --cached --check
git commit -m "Organize project and document final experiments"
```

Chỉ stage/commit sau khi xem danh sách thay đổi. Nhiều đường dẫn cũ có trạng thái `D`, đường dẫn mới là `??` vì đã sắp xếp lại; không tự động có nghĩa là mất dữ liệu. `.gitignore` không loại các file đã được Git theo dõi khỏi lịch sử.
