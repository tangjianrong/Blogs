from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random


def  get_validCode_img(request):
    def random_color():     # 生成随机背景色
        import random
        return (random.randint(0, 255), random.randint(0, 255),
                random.randint(0, 255))
    """
    方式1
    from PIL import Image
    img = Image.new('RGB', (270, 36), color=random_color())
    with open('validCode.png', 'wb') as f:
        img.save(f, 'png')  # 保存图片，加载到磁盘上
    with open('validCode.png', 'rb') as ff:
        data = ff.read()    # 从磁盘读出来

    方式2：直接调用内存，提高速度；完成后系统自动释放内存
    from PIL import Image
    from io import BytesIO
    img = Image.new('RGB', (270, 36), color=random_color())
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    """
    # 方式3：
    img = Image.new('RGB', (270, 36), color=random_color())    # 背景：颜色类型、尺寸、背景色
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype('static/font/kumo.ttf', 35)      # 引进字体样式
    valid_code = ''
    for i in range(4):  # 验证码有5个字符
        num = str(random.randint(0, 9))     # 数字
        alpha = chr(random.randint(65, 122))    # 字母
        k = random.choice([num, alpha])     # 随机选字母或者数字
        draw.text((i*40+40, 3), k, random_color(), font=font, )     # 写入文字内容
        # 每个字符：坐标，字符，颜色，字体样式
        valid_code = valid_code+k   # 保存验证码

    # 保存验证码，一个浏览器存一份
    request.session['valid_code'] = valid_code

    # 利用内存快速保存
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()

    return data
