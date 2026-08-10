# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> **Họ và tên:** Lường Duy Thái
> **Mã học viên:** 2A202601021

---

## Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> Khi deploy lên Production mà quên cấu hình biến `AGENT_API_KEY`, cơ chế "fail fast" làm app sập lập tức (crash loop) khi vừa khởi động, giúp ta phát hiện ra lỗi cấu hình ngay trên dashboard. Nếu để mặc định `"changeme"`, app vẫn khởi chạy bình thường nhưng kẻ xấu có thể đoán được key này để gọi API tự do hoặc gửi các request làm cạn kiệt tài nguyên hệ thống, gây lộ thông tin và thiệt hại chi phí mà ta không hề hay biết.

---

## Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")` không làm được.

> Dòng log JSON thu được:
>
> ```json
> {
>   "timestamp": "2026-08-10T04:00:39.085422+00:00",
>   "level": "info",
>   "event": "ask_completed",
>   "user_id": "sv-2A202601021",
>   "tokens_in": 5,
>   "tokens_out": 42,
>   "cost_usd": 0.000028
> }
> ```
>
> Hai việc làm được với log JSON:
>
> 1. Dễ dàng đẩy log vào các hệ thống tập trung (Elasticsearch, Datadog, Loki) để query, lọc theo `user_id` hoặc cảnh báo tự động khi `cost_usd` tăng đột biến.
> 2. Truy vết và phân tích dữ liệu lượng token tiêu thụ (`tokens_in`, `tokens_out`) cùng chi phí quy đổi tự động để lập báo cáo tài chính/thống kê mức độ sử dụng của từng user.

---

## Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f Dockerfile.single -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản               | Dung lượng |
| ----------------- | ---------- |
| 1 stage (bản đầu) | ~850 MB    |
| Multi-stage       | ~165 MB    |

**Giải thích: phần dung lượng chênh lệch đó là những gì?**

> Phần dung lượng chênh lệch (~685 MB) bao gồm các công cụ biên dịch (gcc, g++, make), bộ nhớ đệm cài đặt của pip (`~/.cache/pip`), các file header/source của C/Python, và các file rác phát sinh trong quá trình build dependency ở Stage 1. Trong Multi-stage build, Stage 2 chỉ copy đúng thư mục thư viện đã cài hoàn chỉnh `/install` sang image `python:3.11-slim` sạch nên image cuối cùng gọn nhẹ hơn rất nhiều.

---

## Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt `COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> Khi sửa `app/main.py` và build lại: Các layer từ base image `FROM`, `WORKDIR`, `COPY requirements.txt` và `RUN pip install` đều được dùng lại từ Docker Cache (vì `requirements.txt` không đổi). Chỉ có các layer từ `COPY app/ app/` trở đi mới phải chạy lại.
>
> Nếu đặt `COPY . .` lên trước `RUN pip install`: Mỗi lần sửa bất kỳ dòng code nào trong dự án, Docker sẽ đánh dấu Cache bị invalid từ bước `COPY . .`, buộc container phải tải và chạy lại lệnh `RUN pip install` rất tốn thời gian.

---

## Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗi hổng trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> **Chuỗi sự kiện:**
>
> 1. Code Python có lỗi RCE (Remote Code Execution) hoặc LFI cho phép kẻ tấn công thực thi lệnh shell bên trong container.
> 2. Vì container chạy mặc định bằng quyền root, kẻ tấn công có toàn quyền đọc/ghi các file hệ thống trong container.
> 3. Kẻ tấn công lợi dụng các lỗ hổng Container Escape (như mount `/var/run/docker.sock` hoặc lọt qua Linux Capabilities) để leo thang đặc quyền ra máy Host với quyền Root của hệ điều hành.
>
> Lệnh `USER appuser` cắt đứt chuỗi tấn công ngay từ Bước 2: khiến lệnh của kẻ tấn công chỉ chạy dưới quyền của một user thường không có đặc quyền (non-root), không thể ghi vào thư mục hệ thống hay thực hiện các thao tác nguy hiểm để escape ra máy Host.

---

## Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được con số đó.

> Tối đa **20 request** trong 2 giây liên tiếp (ở giây 59 của phút trước và giây 00 của phút sau).
>
> **Giải thích:** Với Fixed Window (reset theo mốc giây 00):
>
> - Ở giây 59 của Phút thứ 1: User gửi 10 request liên tiếp (vẫn hợp lệ vì hạn mức Phút 1 là 10).
> - Ngay sang giây 00 của Phút thứ 2: Đếm counter tự động reset về 0. User gửi ngay thêm 10 request nữa (vẫn hợp lệ vì hạn mức Phút 2 là 10).
> - Tổng cộng trong khoảng thời gian 2 giây (từ giây 59 đến giây 00 tiếp theo), user đã gửi thành công 20 request, gấp đôi hạn mức hệ thống cho phép.

---

## Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua nhưng cost guard phải chặn, và một tình huống ngược lại.

> **Khác nhau:**
>
> - **Rate Limit:** Bảo vệ hạ tầng/máy chủ khỏi bị quá tải bằng cách giới hạn tốc độ/tần suất gửi request trong khoảng thời gian ngắn (ví dụ: request/phút).
> - **Cost Guard:** Bảo vệ ngân sách/tài chính bằng cách giới hạn tổng chi phí/token tiêu thụ tích lũy theo chu kỳ dài (ví dụ: USD/tháng).
>
> **Tình huống:**
>
> - _Rate limit cho qua nhưng Cost guard chặn:_ User gửi 1 request duy nhất trong 10 phút (không phạm rate limit), nhưng request này yêu cầu tóm tắt tài liệu 500 trang khiến token tiêu tốn vượt quá ngân sách $10/tháng → Cost guard chặn (402 Payment Required).
> - _Cost guard cho qua nhưng Rate limit chặn:_ User dùng script gửi 30 request ngắn liên tục trong 3 giây (mỗi request hỏi "Hi", tổng tốn $0.001 rất nhỏ so với budget tháng), nhưng tốc độ vượt quá 10 req/phút → Rate limit chặn từ request thứ 11 (429 Too Many Requests).

---

## Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm 3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> **Chuỗi sự kiện xảy ra:**
>
> 1. Ngay khi Redis mất kết nối, endpoint gộp chung trả về lỗi (ví dụ: 500 hoặc 503).
> 2. Orchestrator (K8s/Docker Swarm/Render) đọc kết quả endpoint này làm Liveness Probe và hiểu rằng cả 3 process Python container đã chết.
> 3. Orchestrator lập tức kill toàn bộ 3 container và cố gắng khởi chạy lại (restart loop) liên tục trong suốt 30 giây.
> 4. Việc restart không giải quyết được vấn đề (vì Redis vẫn đang sập), làm tốn tài nguyên CPU/RAM hệ thống và khiến app rơi vào trạng thái CrashLoopBackOff.
> 5. Khi Redis phục hồi sau 30s, các container vẫn mất thêm thời gian khởi động lại từ đầu thay vì ngay lập tức nhận traffic như bình thường.

---

## Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một `X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> Con số `history_length` sẽ thay đổi nhảy vọt và tăng giảm không đều đặn giữa các request (ví dụ: 0 → 0 → 2 → 0 → 2 thay vì 0 → 2 → 4 → 6 → 8).
>
> **Lý do:** Vì Load Balancer (Nginx) điều phối request xoay vòng qua 3 container khác nhau (`agent_1`, `agent_2`, `agent_3`). Mỗi container quản lý một dict Python riêng trong bộ nhớ RAM của nó, không chia sẻ với các container còn lại. Khi request rơi vào container mới chưa từng tiếp nhận user này, dict của container đó trống nên `history_length` lại quay về 0.

---

## Câu 10 — Deploy thật (CP5)

Ghi lại một lỗi bạn gặp khi deploy lên cloud (build fail, health check timeout, sai `REDIS_URL`, app không đọc `$PORT`...): thông báo lỗi là gì, bạn tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> **Thông báo lỗi:** Trên trình duyệt truy cập `/ready` báo `{"status": "not ready", "redis": false}`, hoặc log Render báo `redis.exceptions.ConnectionError: Error -2 connecting to localhost:6379`.
>
> **Cách tìm nguyên nhân:** Vào mục Logs trên Render Dashboard, thấy ứng dụng khi khởi chạy bị dính giá trị mặc định `localhost:6379` trong hàm `get_redis_client()` thay vì đọc chuỗi URL thực tế từ biến môi trường `REDIS_URL`.
>
> **Cách sửa:** Sửa lại hàm `get_redis_client()` trong `app/store.py` để tự động đọc `get_settings().redis_url` từ môi trường, đồng thời cập nhật đúng chuỗi `REDIS_URL` (Upstash/`fake://`) trong phần Environment Variables trên Render Dashboard rồi re-deploy.
