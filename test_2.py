import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Tải và hiển thị hình ảnh với khung tọa độ
img = mpimg.imread(
    "E:/HocTap/graduation_project/waste-detect-project/00480.jpg"
)  # Thay đường dẫn bằng tên tệp ảnh của bạn
fig, ax = plt.subplots()
ax.imshow(img)


# Hàm xử lý sự kiện click vào hình ảnh để lấy tọa độ
def onclick(event):
    if event.xdata and event.ydata:
        x, y = event.xdata, event.ydata
        print(f"Tọa độ của điểm được chọn: ({int(x)}, {int(y)})")


# Kết nối sự kiện click chuột
cid = fig.canvas.mpl_connect("button_press_event", onclick)

plt.show()
