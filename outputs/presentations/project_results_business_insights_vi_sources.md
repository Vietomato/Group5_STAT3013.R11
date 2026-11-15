# Nguồn và cách đọc slide

- Stage 3: `outputs/tables/inferential_statistics/statistical_test_results.csv` — 5 kiểm định, Holm; khoảng cách báo rank-biserial, các chênh lệch khác theo đơn vị ghi trên slide. RQ2/RQ4: Late trừ Not Late; RQ3: ngày lễ trừ ngày thường; RQ5: tỷ lệ đánh giá thấp Late trừ Not Late.
- Stage 4: `outputs/tables/explanatory_regression/five_rq_adjusted_results.csv` — mô hình transformed không thêm lịch là bộ kết quả chính; CI theo cụm 7 ngày, pointwise. RQ5 dùng biến phụ thuộc low_review; 4 RQ còn lại dùng is_late. Holm là một family riêng Stage 4.
- ML Validation A: `outputs/tables/machine_learning/ml_catboost/20261111_152855_922857/baseline_model_comparison.csv`.
- ML Test: `outputs/tables/machine_learning/ml_test/20261111_160038_411032/test_model_comparison.csv`.
- AP là Average Precision, càng cao càng tốt; không phải accuracy. Các giá trị ML trên slide là baseline, xác suất gốc; không trộn kết quả calibration hoặc sampling. CatBoost được chọn trên Validation A; Test chỉ mô tả kết quả đã lưu, không chọn lại mô hình. Mô hình học máy vẫn có AP thấp.
- Dữ liệu Stage 3, mẫu complete-case training Stage 4, Validation A và Test khác nhau. Không diễn giải các cột như cùng một mẫu.

File PowerPoint có 9 slide với nội dung chỉnh sửa được. PNG là bản xem trước được tạo từ cùng nội dung và tọa độ; không phải ảnh xuất bằng PowerPoint.


## Additional sources for the nine-slide deck

- Slide 2: sample accounting from Stage 3 and Stage 4 tables; Train/Validation/Test definitions from data/ml_preparation/split_manifest.csv and split_summary.csv.
- Slide 4: calendar rainfall sensitivity from outputs/tables/explanatory_regression/five_rq_sensitivity_results.csv. Review-state groups with fewer than 100 retained review orders were pooled after a rare-level fit instability. Review regression is retrospective.
- Slide 6: outputs/tables/machine_learning/ml_random_undersampling/20261111_161215_292137/sampling_method_comparison.csv. AP, Brier and LogLoss refer to Validation A. Sampling trials followed Test exposure and are exploratory.
- Slide 7: outputs/tables/machine_learning/ml_test/20261111_160038_411032/selected_threshold_metrics.csv. These are calibrated CatBoost results at the frozen Validation B threshold, unlike the raw baseline probability comparison on Slide 5. No Test retuning was performed.
- Slides 8 and 9: proposed operational implications and future pilot actions, not measured intervention effects, realised financial benefits or deployment claims. Prioritising long routes/customer care should be validated with operational data and a controlled pilot.

The PPTX contains nine editable slides. XML syntax, package relationships, ZIP integrity and preview text widths were checked. PNG previews are generated from the same layout, not rendered by PowerPoint. No model was retrained for this presentation.
