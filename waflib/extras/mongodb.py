#! /usr/bin/env python
# encoding: utf-8

'''

When using this tool, the wscript will look like:

	def options(opt):
	        opt.load('boost mongodb')

	def configure(conf):
		conf.load('compiler_cxx boost mongodb')
                conf.check_boost ('system filesystem thread')
                conf.check_mongodb ()

	def build(bld):
		bld(source='main.cpp', target='app', use='MONGODB')

Options are generated, in order to specify the location of ccnx includes/libraries.


'''
import sys
import re
from waflib import Utils,Logs,Errors
from waflib.Configure import conf
MONGODB_DIR=['/usr','/usr/local','/opt/local','/sw']
MONGODB_VERSION_FILE='mongo/util/version.h'
MONGODB_VERSION_CODE='''
#include <mongo/client/dbclient.h>
#include <mongo/util/version.h>
#include <iostream>
int main() 
{
    mongo::DBClientConnection c;
    sizeof (c);
    return 0; 
}
'''

def options(opt):
	opt.add_option('--mongodb',type='string',default='',
                       dest='mongodb_dir',help='''path to where mongodb is installed, e.g. /usr/local''')

@conf
def check_mongodb(self,*k,**kw):
	if not self.env['CXX']:
		self.fatal('load a cxx compiler first, conf.load("compiler_cxx")')

	var=kw.get('uselib_store','MONGODB')
	self.start_msg('Checking MongoDB')

        self.env['LIB_%s' % var] = "mongoclient"
        self.define ("_FILE_OFFSET_BITS", 64)
        self.define ("FUSE_USE_VERSION", 26)

        for dir in Utils.to_list (MONGODB_DIR):
                self.env['LIBPATH_%s' % var] = "%s/lib" % dir
                self.env['INCLUDES_%s'% var] = "%s/include" % dir
        
                ok = self.check_cxx(fragment=MONGODB_VERSION_CODE,
                                    use=[var, "BOOST", "BOOST_THREAD", "BOOST_SYSTEM", "BOOST_FILESYSTEM"],
                                    mandatory=False, execute = True)
                if ok:
                        break

        if not ok and kw.get('Mandatory',True):
                del self.env['LIB_%s' % var]
                del self.env['LIBPATH_%s' % var]
                del self.env['INCLUDES_%s'% var]

                self.fatal ("Cannot find MongoDB library", 'YELLOW')

        self.end_msg ("Found in %s" % dir)
