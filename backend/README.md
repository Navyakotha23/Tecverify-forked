# Setup

D:\>`mkdir tecverify`

`D:\>cd tecverify`

`D:\tecverify>git clone https://gitlab.tecnics.com/tec-sso-web-app/tecverify-master.git`

## Virtual Environment
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated python virtual environments for them. This is one of the most important tools that most of the Python developers use.

`D:\tecverify>cd tecverify-master`

If python is installed in your system, then pip comes in handy.
So simple steps are:
1) Install virtualenv using

 `D:\tecverify\tecverify-master>pip install virtualenv`
2)Now in which ever directory you are, this line below will create a virtualenv there

 `D:\tecverify\tecverify-master>virtualenv myenv`
And here also you can name it anything.

3) Now if you are same directory then type,

  `D:\tecverify\tecverify-master>myenv\Scripts\activate`
You can explicitly specify your path too.

After you activate, command prompt will be modified as below:
`(myenv) D:\tecverify\tecverify-master>` 

## Installing Requirements

If you are in tecverify-master directory, then you can notice requirements.txt.

Using pip and requirements.txt, installing required packages becomes simple.

`(myenv) D:\tecverify\tecverify-master>pip install -r requirements.txt`

## Starting Development Server

`(myenv) D:\tecverify\tecverify-master>python server.py`
