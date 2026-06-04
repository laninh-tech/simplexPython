# QHTT Studio — Chương Trình Giải Bài Toán Quy Hoạch Tuyến Tính Tổng Quát

> 🌐 **Demo trực tuyến (Live App)**: [https://simplexpython.onrender.com/](https://simplexpython.onrender.com/)

**QHTT Studio** là một ứng dụng web trực quan, hiện đại được thiết kế để giải quyết các bài toán Quy hoạch tuyến tính (QHTT) dạng tổng quát. Chương trình không chỉ trả về kết quả tối ưu cuối cùng mà còn hiển thị chi tiết các bảng lặp đơn hình (bảng xoay cơ sở) và biểu diễn hình học miền khả thi trên mặt phẳng 2D, giúp người dùng (sinh viên, giảng viên) dễ dàng học tập và giảng dạy môn học Quy hoạch tuyến tính / Toán tối ưu / Vận trù học.

Dự án được xây dựng bởi nhóm sinh viên **Khoa Toán - Tin học**, **Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM** phục vụ đồ án môn học.

---

## 🌟 Các Tính Năng Nổi Bật

- **Nhập liệu linh hoạt**: Hỗ trợ bài toán với số lượng biến số và ràng buộc tùy ý. Chấp nhận các biểu thức toán học trực tiếp tại ô nhập hệ số (ví dụ: `sqrt(9)`, `3/2`, `exp(0)`, `pi`, `abs(-3)`).
- **Hỗ trợ điều kiện biên đa dạng**:
  - Biến không âm: $x_j \ge 0$
  - Biến không dương: $x_j \le 0$
  - Biến tự do (tùy ý về dấu)
- **Đa dạng phương pháp giải**:
  - **Simplex Hai Pha (Two Phase)**: Dành cho các bài toán chưa có nghiệm cơ sở khả thi xuất phát (ràng buộc hỗn hợp $\ge$, $\le$, $=$).
  - **Simplex Tiêu Chuẩn (Dantzig)**: Quy tắc xoay chọn phần tử cải thiện tốt nhất.
  - **Simplex Xoay Vòng (Bland)**: Hạn chế hiện tượng xoay vòng vô hạn đối với các bài toán suy biến.
  - **Phương Pháp Hình Học (Đồ thị 2D)**: Dành cho bài toán 2 biến, trực quan hóa miền khả thi, các đỉnh khả thi và đường đi của thuật toán đơn hình.
- **Giao diện người dùng Premium**:
  - Phong cách thiết kế kính mờ (Glassmorphism), chuyển động hạt nền mượt mà.
  - **Hỗ trợ chế độ tối toàn diện (Dark Mode)**: Tự động chuyển đổi màu sắc giao diện, bảng đơn hình và đồ thị Plotly tương ứng.
  - Công thức toán học kết xuất sắc nét bằng **KaTeX**.
  - Font chữ **Be Vietnam Pro** và **Inter** hiển thị tiếng Việt chuẩn hóa, không lỗi font.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python 3, Flask (Web server), Numpy (Tính toán ma trận đơn hình số học).
- **Frontend**: HTML5, Vanilla CSS3 (Custom variables), JavaScript (ES6).
- **Thư viện trực quan**: Plotly.js (Vẽ đồ thị 2D động), KaTeX (Biểu diễn công thức toán học).

---

## 🚀 Hướng Dẫn Khởi Chạy

### Cách 1: Chạy tự động trên Windows (Khuyên dùng)
Nếu bạn đang sử dụng hệ điều hành Windows, chỉ cần nhấp đúp chuột vào tập tin:
```bash
run_web_demo.bat
```
Tập tin này sẽ tự động:
1. Kiểm tra môi trường Python.
2. Cài đặt các thư viện phụ thuộc từ `requirements.txt` nếu chưa có.
3. Giải phóng tiến trình cũ đang chiếm dụng cổng `8080` (nếu có).
4. Khởi động server Flask tại địa chỉ `http://localhost:8080`.

### Cách 2: Khởi chạy thủ công từ dòng lệnh
Nếu bạn chạy trên các hệ điều hành khác hoặc muốn chạy thủ công:
1. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
2. Thiết lập đường dẫn môi trường ( PYTHONPATH) về thư mục cha của dự án và chạy:
   ```bash
   # Di chuyển vào thư mục cha của simplexPython
   cd path/to/project_root
   
   # Chạy app Flask dưới dạng package
   python -m simplexPython.menu.app
   ```
3. Truy cập địa chỉ [http://localhost:8080](http://localhost:8080) trên trình duyệt của bạn.

---

## 👥 Nhóm Thực Hiện Dự Án

* **La Quãng Ninh** (MSSV: 21110362)
  * *Nhiệm vụ*: Nghiên cứu lý thuyết, phát triển giao diện web, lập trình logic & bộ giải thuật toán đơn hình.
* **Nguyễn Phi Hùng** (MSSV: 24110165)
  * *Nhiệm vụ*: Kiểm thử chất lượng thuật toán, biên soạn tài liệu kỹ thuật và báo cáo dự án.

#### Giảng viên hướng dẫn:
* **Thầy Nguyễn Lê Hoàng Anh**
* Khoa Toán - Tin học — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM.
* Thời gian hoàn thành: **Tháng 06/2026**.


