#! /usr/bin/env python
# encoding: utf-8

'''

When using this tool, the wscript will look like:

	def options(opt):
	        opt.tool_options('ndnx')

	def configure(conf):
		conf.load('compiler_c ndnx')

	def build(bld):
		bld(source='main.cpp', target='app', use='NDNX')

Options are generated, in order to specify the location of ndnx includes/libraries.


'''
import sys
from waflib import Utils, Logs, Errors, Options, ConfigSet
from waflib.Configure import conf

NDNX_DIR=['/usr','/usr/local','/opt/local','/sw']
NDNX_VERSION_FILE='ccn/ccn.h'
NDNX_VERSION_CODE='''
#include <ccn/ccn.h>
#include <stdio.h>
int main() { printf ("%d.%d.%d", ((CCN_API_VERSION/100000) % 100), ((CCN_API_VERSION/1000) % 100), (CCN_API_VERSION % 1000)); return 0; }
'''

@conf
def __ndnx_get_version_file(self,dir):
	# Logs.pprint ('CYAN', '  + %s/%s/%s' % (dir, 'include', NDNX_VERSION_FILE))
	try:
		return self.root.find_dir(dir).find_node('%s/%s' % ('include', NDNX_VERSION_FILE))
	except:
		return None
@conf
def ndnx_get_version(self,dir):
	val=self.check_cc(fragment=NDNX_VERSION_CODE,includes=['%s/%s' % (dir, 'include')],execute=True,define_ret = True, mandatory=True)
	return val
@conf
def ndnx_get_root(self,*k,**kw):
	root=Options.options.ndnx_dir or (k and k[0]) or kw.get('path',None)
        
	if root:
                if self.__ndnx_get_version_file(root):
                        return root
		self.fatal('NDNx not found in %s'%root)
                
	for dir in NDNX_DIR:
		if self.__ndnx_get_version_file(dir):
			return dir
        self.fatal('NDNx not found, please provide a --ndnx argument (see help)')

@conf
def check_openssl(self,*k,**kw):
        root = k and k[0] or kw.get('path',None) or Options.options.openssl
        mandatory = kw.get('mandatory', True)
        var = kw.get('var', 'SSL')

        if root:
                self.check_cc (lib='crypto ssl',
                               header_name='openssl/crypto.h',
                               define_name='HAVE_%s' % var,
                               uselib_store=var,
                               mandatory = mandatory,
                               cflags="-I%s/include" % root,
                               linkflags="-L%s/lib" % root)
        else:
                libcrypto = self.check_cc (lib='crypto ssl',
                                           header_name='openssl/crypto.h',
                                           define_name='HAVE_%s' % var,
                                           uselib_store=var,
                                           mandatory = mandatory)
                
        #         # env = self.env
        #         # self.env.env = {"PKG_CONFIG_PATH": "%s/lib/pkgconfig" % root}
        #         # try:
        #         #         libcrypto = self.check_cfg (package='openssl', args=['--cflags', '--libs'], 
        #         #                                     uselib_store=var, mandatory=True,
        #         #                                     env = env)
        #         # except:
        #         #         try:
        #         #                 libcrypto = self.check_cfg (package='ssl', args=['--cflags', '--libs'], 
        #         #                                             uselib_store=var, mandatory=True,
        #         #                                             env = env)
        #         #         except:
        #         #                 libcrypto = self.check_cc (lib='crypto ssl',
        #         #                                            header_name='openssl/crypto.h',
        #         #                                            define_name='HAVE_%s' % var,
        #         #                                            uselib_store=var,
        #         #                                            mandatory = mandatory,
        #         #                                            cflags="-I%s/include" % root,
        #         #                                            linkflags="-L%s/lib" % root)
        #         #                 if not libcrypto:
        #         #                         raise
        #         # else:
        #         #         self.define ("HAVE_%s" % var, 1)
        # else:
        #         try:
        #                 libcrypto = self.check_cfg (package='openssl', args=['--cflags', '--libs'], 
        #                                             uselib_store=var, mandatory=True)
        #         except:
        #                 try:
        #                         libcrypto = self.check_cfg (package='ssl', args=['--cflags', '--libs'], 
        #                                                     uselib_store=var, mandatory=True)
        #                 except:
        #                         libcrypto = self.check_cc (lib='crypto ssl',
        #                                                    header_name='openssl/crypto.h',
        #                                                    define_name='HAVE_%s' % var,
        #                                                    uselib_store=var,
        #                                                    mandatory = mandatory)
        #                 if not libcrypto:
        #                     raise
        #         else:
        #                 self.define ("HAVE_%s" % var, 1)

        # if not self.get_define ("HAVE_%s" % var):
        #         self.fatal ("Cannot find SSL libraries")

@conf
def check_ndnx(self,*k,**kw):
	if not self.env['CC']:
		self.fatal('load a c compiler first, conf.load("compiler_c")')

	var=kw.get('uselib_store', 'NDNX')
	self.start_msg('Checking for NDNx')
	root = self.ndnx_get_root(*k,**kw);
	self.env.NDNX_VERSION=self.ndnx_get_version(root)

	self.env['INCLUDES_%s' % var]= '%s/%s' % (root, "include");
	self.env['LIB_%s' % var] = "ccn"
	self.env['LIBPATH_%s' % var] = '%s/%s' % (root, "lib")

        self.env['%s_ROOT' % var] = root

	self.end_msg("%s in %s " % (self.env.NDNX_VERSION, root))
	if Logs.verbose:
		Logs.pprint('CYAN','	NDNx include : %s'%self.env['INCLUDES_%s' % var])
		Logs.pprint('CYAN','	NDNx lib     : %s'%self.env['LIB_%s' % var])
		Logs.pprint('CYAN','	NDNx libpath : %s'%self.env['LIBPATH_%s' % var])

def options(opt):
        """
        NDNx options
        """
        ndnopt = opt.add_option_group("NDNx Options")
	ndnopt.add_option('--ndnx',type='string',default=None,dest='ndnx_dir',help='''path to where NDNx is installed, e.g. /usr/local''')
        ndnopt.add_option('--openssl',type='string',default='',dest='openssl',help='''path to openssl, should be the same NDNx is compiled against''')
