# Lab 3: Triển khai /orders có cursor pagination

## Kiểm thử

### Test 1: Lọc theo status (`status=paid`)

![Test 1](Testpng/Test1.png)

### Test 2: Phân trang Cursor pagination (`limit=5`)

![Test 2](Testpng/Test2.png)

### Test 3: Sparse fieldsets (`fields=id,total`)

![Test 3](Testpng/Test3.png)

### Test 4: Cursor không hợp lệ → 400 Bad Request

![Test 4](Testpng/Test_404_cursor.png)
