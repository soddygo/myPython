
from distutils.core import setup

setup(name='myPython',  #打包后的包文件名
      version='1.0',
      description='My python demo',
      author='soddy',
      author_email='soddygo@gmail.com',
      # url='http://blog.liuts.com',
      py_modules=['weixin.wxConfig','weixin.NotifyByWeixin'],   #与前面的新建文件名一致
)