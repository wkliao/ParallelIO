from __future__ import generators
import os
import subprocess
import environment as lmod
import abc

class platformBuilder(object):
    """ abstract base class that implements interfaces and 
        a factory pattern.  creates a relevant
        platform class (darwin_gnu, yellowstone_intel, goldbach_nag, etc... that
        configures cmake, builds pio and tests, and runs the unit tests
    """
    __metaclass__  = abc.ABCMeta
    TEST_CMD = 'ctest'
    MAKE_CMD = 'make all'
    
    @classmethod
    def _raise_not_implemented(cls, method_name):
        raise NotImplementedError(
                                  cls.__name__ +" does not implement method "+method_name+".")
    
    @abc.abstractmethod
    def runModuleCmd(self, modname):
        """Method not implemented."""
        self._raise_not_implemented("runModuleCmd")
    
    @abc.abstractmethod
    def cmakeCmd(self):
        """Method not implemented."""
        self._raise_not_implemented("cmakeCmd")
    
    def metaBuild(self):
        """ routine where everything gets kicked off from
        """
        self.runModuleCmd()
        self.cmakeCmd()
        self.buildCmd()
        self.testCmd()
    
    def buildCmd(self):
        """ run build
        """
        p = subprocess.Popen(self.MAKE_CMD,
                             shell=True, env=self.envMod)
        p.wait()
    
    def testCmd(self):
        """ run tests
        """
        p = subprocess.Popen(self.TEST_CMD,
                             shell=True, env=self.envMod)
        p.wait()
    
    def factory(type):
        """ factory method for instantiating the appropriate class
        """
        if type == "darwin_gnu":
            return darwin_gnu()
        if type == "yellowstone_intel":
            return yellowstone_intel()
        assert 0, "build platform not supported: " + type
    factory = staticmethod(factory)


class darwin_gnu(platformBuilder):

    CMAKE_EXE = '/opt/local/bin/cmake'
    BUILD_DIR = 'build'
    

    FC = '/opt/local/bin/mpifort-mpich-gcc48'
    CC = '/opt/local/bin/mpicc-mpich-mp'
    LDFLAGS = '-lcurl'

    FFLAGS = (' -D CMAKE_Fortran_FLAGS:STRING="-O -fconvert=big-endian '
              '-ffree-line-length-none -ffixed-line-length-none '
              '-fno-range-check '
              '-g -Wall  -DDarwin  -DMCT_INTERFACE -DNO_MPI2 -DNO_MPIMOD '
              '-DFORTRANUNDERSCORE -DNO_R16 -DSYSDARWIN  -DDarwin '
              '-DCPRGNU -I. " ')
    CFLAGS = ('-D CMAKE_C_FLAGS:STRING=" -DDarwin  -DMCT_INTERFACE -DNO_MPI2 '
              '-DNO_MPIMOD -DFORTRANUNDERSCORE -DNO_R16 -DSYSDARWIN  -DDarwin '
              '-DCPRGNU -I. " ')
    OFLAGS = ('-D CMAKE_VERBOSE_MAKEFILE:BOOL=ON -D '
              'NETCDF_DIR:STRING=/opt/local '
              '-D WITH_PNETCDF:LOGICAL=FALSE -D '
              'PIO_BUILD_TESTS:LOGICAL=TRUE ')
    CTEST_EXE = ' -D  MPIEXEC:FILEPATH=/opt/local/bin/mpiexec-mpich-gcc48 '

    envMod = {}

    def runModuleCmd(self):
        """ run module cmds
        """
        # ~# not implemented for a system without lmod (or
        # ~# somthing similar)
        pass

    def cmakeCmd(self):
        """ cmake command to run
        """
        # ~# make build directory and move to it.
        if not os.path.exists(self.BUILD_DIR):
            os.makedirs(self.BUILD_DIR)

        os.chdir(self.BUILD_DIR)

        # ~# change environemnt, first get existing env
        self.envMod = dict(os.environ)
        # ~# add to env
        self.envMod['FC'] = self.FC
        self.envMod['CC'] = self.CC
        self.envMod['LDFLAGS'] = self.LDFLAGS

        cmakeString = (self.CMAKE_EXE + self.FFLAGS + self.CFLAGS +
                       self.OFLAGS + self.CTEST_EXE + ' ..')
        p = subprocess.Popen(cmakeString,
                             shell=True, env=self.envMod)
        p.wait()

    def buildCmd(self):
        """ run build
        """
        p = subprocess.Popen(self.MAKE_CMD,
                             shell=True, env=self.envMod)
        p.wait()


class yellowstone_intel(platformBuilder):

    moduleList = ['intel/14.0.2',
                  'ncarcompilers/1.0',
                  'netcdf-mpi/4.3.0',
                  'pnetcdf/1.4.1',
                  'ncarenv/1.0',
                  'cmake',
                  'ncarbinlibs/1.1']

    CMAKE_EXE = 'cmake'
    BUILD_DIR = 'build'
    

    FC = 'mpif90'
    CC = 'mpicc'
    LDFLAGS = ''

    FFLAGS = (' -D CMAKE_Fortran_FLAGS:STRING="-fp-model source '
              '-convert '
              'big_endian -assume byterecl -ftz -traceback -assume '
              'realloc_lhs '
              '-xHost  -O2   -DLINUX  -DNDEBUG -DMCT_INTERFACE '
              '-DHAVE_MPI '
              '-DFORTRANUNDERSCORE -DNO_R16 -DHAVE_NANOTIME  -DLINUX '
              '-DCPRINTEL '
              '-DHAVE_SLASHPROC -I. " ')
    CFLAGS = (' -D CMAKE_C_FLAGS:STRING="-O2 -fp-model precise -xHost '
              '-DLINUX  -DNDEBUG -DMCT_INTERFACE -DHAVE_MPI '
              '-DFORTRANUNDERSCORE -DNO_R16 -DHAVE_NANOTIME  -DLINUX '
              '-DCPRINTEL  -DHAVE_SLASHPROC -I. " ')
    OFLAGS = ('-D CMAKE_VERBOSE_MAKEFILE:BOOL=ON '
              '-D NETCDF_DIR:STRING='
              '/glade/apps/opt/netcdf-mpi/4.3.2/intel/default '
              '-D PIO_FILESYSTEM_HINTS:STRING=gpfs '
              '-D PIO_BUILD_TESTS:LOGICAL=TRUE ')

    QUEUE = ('-D QUEUE:FILEPATH=execca ')
    MPIEXEC = ('-D MPIEXEC:FILEPATH=mpirun.lsf ')

    envMod = {}

    def runModuleCmd(self):
        """ run module cmds
        """
        self.lmod = lmod.ModuleInterface()
        self.lmod.python_init("/glade/apps/opt/lmod/lmod/init/"
                              "env_modules_python.py")
        self.lmod.purge()

        for cmd in self.moduleList:
            self.lmod.load(cmd)

    def cmakeCmd(self):
        """ cmake command to run
        """
        # ~# make build directory and move to it.
        if not os.path.exists(self.BUILD_DIR):
            os.makedirs(self.BUILD_DIR)

        os.chdir(self.BUILD_DIR)
        # ~#
        ### self.runModuleCmd()

        # ~# change environemnt, first get existing env
        self.envMod = dict(os.environ)
        # ~# add to env
        self.envMod['FC'] = self.FC
        self.envMod['CC'] = self.CC
        self.envMod['LDFLAGS'] = self.LDFLAGS

        cmakeString = (self.CMAKE_EXE + self.FFLAGS + self.CFLAGS +
                       self.OFLAGS + self.QUEUE + self.MPIEXEC + ' ..')

        print cmakeString
        p = subprocess.Popen(cmakeString,
                             shell=True, env=self.envMod)
        p.wait()



