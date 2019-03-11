import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


class Image2CharStyle:
    def __init__(self, width, height, fontfile, filepath, savepath):
        self.charset = "$@B%8&WM#*oahkbdpqwmzcvunxrjft/\\|()1{}[]?-_+~<>i!;:,\"^`'. "
        self.width = width
        self.height = height
        self.filepath = filepath
        self.savepath = savepath
        self.fontfile = fontfile
        self.charset2 = self.charset256(self.charset)

    @staticmethod
    def load_font(font_file, font_size=128):
        """
        加载字体
        """
        return ImageFont.truetype(open(font_file, 'rb'), size=font_size, encoding='utf-8')

    @staticmethod
    def plot_char(canvas_size, offset, char, font, color, white=(255, 255, 255), img_type='RGB'):
        """
        绘制字符
        """
        image = Image.new(img_type, (canvas_size, canvas_size), white)
        draw = ImageDraw.Draw(image)
        draw.text((offset, offset), char, color, font=font)
        return np.array(image)

    @staticmethod
    def charset256(charset):
        """
        将字符集扩展到256
        """
        charset_len = len(charset)
        if charset_len > 256:
            return charset[:256]
        r = 256 // charset_len
        m = 256 % charset_len
        s = ''
        for i in charset[:m]:
            s += i * (r + 1)
        for i in charset[m:]:
            s += i * r
        return s

    def gif2char(self):
        """
        处理GIF图片，按帧拆分处理
        """
        gif = Image.open(self.filepath)
        # print(gif.info['duration'])
        gif.seek(1)
        char_set = []
        color_set = []
        try:
            while True:
                char, color = self.image2char(gif, False)
                char_set.append(char)
                color_set.append(color)
                gif.seek(gif.tell() + 1)
        except EOFError:
            return char_set , color_set

    def image2char(self, image, flag=True):
        """
        计算各像素处的字符
        """
        if flag:
            image = Image.open(image)
        image = image.convert('RGB')
        img_rgb = image.resize((self.width, self.height))
        img_gray = img_rgb.convert('L')
        pix_gray = img_gray.load()
        pix_rgb = img_rgb.load()
        char_set = []
        color_set = []
        for i in range(self.height):
            for j in range(self.width):
                char = self.charset2[pix_gray[j, i]]
                char_set.append(char)
                color_set.append(pix_rgb[j, i])
        return char_set, color_set

    def char2image(self, char_set, pix):
        """
        将字符转化为图像
        """
        images = []
        try:
            font = self.load_font(self.fontfile, 10)
            for i, char in enumerate(char_set):
                color = pix[i]
                color = tuple(color)
                images.append(self.plot_char(10, 0, char, font, color))
        except Exception:
            print('failed')
        big_image = np.vstack([np.hstack(images[i:i + self.width])
                               for i in range(0, len(char_set), self.width)])
        return big_image

    def run(self):
        if self.filepath.split('.')[-1] != 'gif':
            chars, color = self.image2char(self.filepath)
            img = self.char2image(chars, color)
            imageio.imsave(self.savepath, img)
        else:
            chars, colors = self.gif2char()
            imgs = []
            for i in range(len(chars)):
                img = self.char2image(chars[i], colors[i])
                imgs.append(img)
            imageio.mimsave(self.savepath, imgs, duration=0.1)
