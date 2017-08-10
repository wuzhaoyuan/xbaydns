About xBayDNS
=============

xBayDNS是一个基于Web的BIND 9管理界面。与通常我们所知道的管理界面所不同的是，它尽可能的将DNS的管理简化，并帮助用户建立起一个容易管理、维护、
扩展的DNS系统。

一个普通的DNS服器可以提供域名的解析、代理、缓存这样的服务。我们期望DNS不但是一个服务，它更应该承担起GSLB、用户访问加速这样的任务。而在现实的环境中，
应用DNS已经能够很好的完成这样的工作。所以沿着从前的经历，我们启动了xBayDNS这个项目，它的目的是让DNS服务在承担着GSLB和访问加速这样的工作时更容
易管理。做为xBayDNS附加的礼物，也可以从中学到如何形成一个基于DNS的GSLB和用户访问加速的原理。

xBayDNS的特性如下：
 * 基于Web的BIND管理
 * 非常容易的支持多种操作系统（现有我们考虑支持的就有FreeBSD、OpenBSD、MacOSX、Linux）
 * 支持ACL、View、TSIG这样的BIND高级管理功能

什么时候使用xBayDNS？
 * 你需要简单的管理一台BIND的DNS服务器
 * 你需要多台DNS服务器来为你的用户提供解晰服务
 * 一套基于DNS的GSLB系统
 * 一套基于DNS的分布式GSLB系统
 * 你需要维护多台分布式的服务器

Install
=============

xBayDNS需要以下软件：
 * BIND （>9.4.1）
 * Django （0.96.1）
 * dnspython （1.6）
 * python（2.5）
 * setuptool

1.安装xbaydns基础系统
下载xbaydnsx.x.tar.gz，将它解压，执行安装脚本：
python setup.py install
它将会把xbaydns的基础系统安装到你的操作系统中。

2.初始化BIND配置
执行xbdinit，它会初始化操作系统中的BIND相关配置。对于不同操作系统，我们还需要你自己确认操作系统的BIND的启动设备：
	FreeBSD
	/etc/rc.conf中设置了 named_enable="YES"你可以使用
	/etc/rc.d/named restart
	了解是不是能正常启动bind。

	Mac OSX 10.5
	使用launchctl  load了org.isc.named的job。你可以使用
	service org.isc.named stop
	service org.isc.named start
	了解是不是能正常启动bind。

3.启动xBayDNS WebAdmin
在解开的包中有一个目录叫xbaydnsweb，在其中有全套的web系统，安装好Django后，到这个目录中执行：
python manage.py runserver
缺省的，登录管理系统的帐号为admin，它的密码也是admin。

4。将xBayDNS的sync加入crontab中
你希望用户增加的域名多久生效就在crontab中设置多久运行一次，运行这个sync脚本需要root权限，脚本为
xbdsync
它通常在/usr/local/bin中

Release Notes
=============

1.0
 * 支持FreeBSD 7.0操作系统
 * 支持Mac OSX 10.5操作系统
 * 支持BIND 9.4.1P1
 * 支持DNS的初始化操作
 * 支持DNS的A、MX、NS、CNAME记录的管理
 * 支持ACL的管理
 * 支持View的管理
 * 支持基于View（TSIG）的域名记录管理