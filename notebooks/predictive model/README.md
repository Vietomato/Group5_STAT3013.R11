# Chạy hai mô hình của Phong

Mở Terminal trong thư mục gốc project. Chạy lần lượt:

```powershell
python -m venv .venv-phong
.\.venv-phong\Scripts\python.exe -m pip install -r "notebooks/predictive model/requirements-phong.txt"
.\.venv-phong\Scripts\python.exe "notebooks/predictive model/train_phong_models.py"
```

Khuyến nghị Python 3.8–3.11 cho bộ phiên bản đã cố định. Không cần kích hoạt môi trường vì gọi trực tiếp python.exe.

Script huấn luyện Logistic Regression và Random Forest gốc với seed 42. Đọc đúng 21 predictors và manifest hiện có; không chia lại, không sửa dataset. Chỉ fit Train, chỉ chấm Validation A. B/Test được kiểm tra số đơn nhưng không được dự đoán hoặc dùng chọn cấu hình. Imputer/encoder/scaler chỉ học trên Train. LR có scaling, RF không scaling. Không trọng số hoặc SMOTE ở bước này.

Mỗi lần chạy có thư mục thời gian riêng:
- outputs/tables/ml_phong/<thời gian>/: metrics, validation predictions, audit, tham số, phiên bản và hash đầu vào.
- outputs/models/ml_phong/<thời gian>/: hai pipeline đã học.
- outputs/figures/ml_phong/<thời gian>/: PR curve trên Validation A.

Đọc validation_a_metrics.csv: AP là Average Precision và là chỉ số so sánh chính; ROC_AUC cao hơn tốt hơn, Brier/LogLoss thấp hơn tốt hơn. Không diễn giải điểm validation như kết quả test độc lập.

Đây là Task 15, chưa phải toàn bộ Stage 5. Sau khi có LightGBM/XGBoost của Việt mới chọn leader chung và thử đúng một cấu hình có trọng số; sau đó calibration/ngưỡng trên B và đánh giá test theo kế hoạch cập nhật. Không chọn winner chung chỉ từ hai mô hình này.

Các predictors Conditional được sử dụng theo giả định thông tin có sẵn lúc mua. Thời gian công bố thời tiết chưa xác minh. Đọc predictor_list.csv và ml_protocol.md cho giới hạn dữ liệu; phần 8 cấu hình/tuning rộng trong protocol cũ khác kế hoạch cập nhật 5 cấu hình. Script này không thực hiện phần đó.


Code nằm trong notebooks/predictive model. Nhánh làm việc: predictive-model. Người dùng tự thực hiện commit.
