#!/usr/bin/env python
#
# Remotely access the NEOS server
# D. Orban,  Montreal, Sept. 2005
# Updated Feb. 2006 to use OptParse

import sys

class NeosInterface:
    """
    An abstract class for connections with the remote NEOS Server for
    Optimization. NeosInterface objects communicate with the NEOS Server via
    XML-RPC. This class wraps the server's services into a few convenient
    methods which, for the time being, are designed with the solution of AMPL
    models in mind.
    """
 
    def __init__( self, **kwargs ):
        import xmlrpclib

        #from config import Variables
        NEOS_HOST = "neos.mcs.anl.gov"
        NEOS_PORT = 3332

        if 'neos_host' in kwargs.keys():
            NEOS_HOST = kwargs['neos_host']
        if 'neos_port' in kwargs.keys():
            NEOS_PORT = kwargs['neos_port']

        neos_url = 'http://%-s:%-d' % (NEOS_HOST, NEOS_PORT)
        neos_server = xmlrpclib.Server( neos_url )

        status = neos_server.ping()
        if status != 'NeosServer is alive\n':
            self.connected = False
            self.server = None
            self.version = None
        else:
            self.connected = True
            self.server = neos_server
            self.version = self.server.version()

        return

#===============================================================================#

    def Connected( self ):
        """
        Connected() returns True if the connection with the NEOS Server was
        successfully established, and False otherwise. This return value should
        be checked before information is sent to, or queried from the server.
        """
        return self.connected

#===============================================================================#

    def GetQueue( self ):
        """
        Returns a string containing the current job queue.
        """
        if self.connected:
            return self.server.printQueue()
        return None

#===============================================================================#

    def GetServerMethods( self ):
        """
        This general method returns a dictionnary listing all the services
        offered by an XML-RPC-compliant server. In the present case, it returns
        the (lenghty) list of all methods exported by the NEOS Server.
        """
        if self.connected:
            server_methods = {}
            for method in self.server.system.listMethods():
                server_methods[method] = self.server.system.methodHelp(method)
            return server_methods
        return None

#===============================================================================#

    def PrintServerMethods( self ):
        """
        Displays the result of GetServerMethods() on standard output.
        """
        server_methods = self.GetServerMethods()
        if server_methods is not None:
            for method in server_methods.keys():
                sys.stdout.write( method + '\n' )
                sys.stdout.write( server_methods[method] )
                sys.stdout.write( '\n' )
                #sys.stdout.write( '\n' + 80*'=' + '\n\n' )
        return None

#===============================================================================#

    def PrintDictionary( self, d ):
        """
        Pretty-print the contents of a dictionary, such as the return value
        of GetServerMethods() or GetAmplSolvers().
        """
        if d is not None:
            for k in d.keys():
                sys.stdout.write( k + '\n  ' + repr(d[k]) + '\n\n' )
        return None

#===============================================================================#

    def GetCategories( self ):
        """
        Returns all solver categories.
        """
        if self.connected:
            return self.server.listCategories()
        return None

#===============================================================================#

    def GetInputFormats( self ):
        """
        Returns all accepted input formats.
        """
        if self.connected:
            all_solvers = self.server.listAllSolvers()
            formats = []
            for solver in all_solvers:
                format = solver.split(':')[2]
                if format not in formats: formats.append(format)
            return formats
        return None
        
#===============================================================================#

    def GetAmplSolvers( self ):
        """
        Returns a dictionnary of elements of the form
          category : [list of solvers in this category accepting AMPL input]
        If no solver accepts AMPL input in some category, the list will be empty.
        """
        if self.connected:
            categories = self.server.listCategories()
            ampl_solvers = {}
            for category in categories.keys():
                #ampl_solvers[category] = []
                fullname = categories[category]
                thiskey = fullname + ' (' + category + ')'
                ampl_solvers[thiskey] = []
                cat_solvers = self.server.listSolversInCategory( category )
                for solver in cat_solvers:
                    name, input = solver.split(':')
                    if input == 'AMPL':
                        #ampl_solvers[category].append( name )
                        ampl_solvers[thiskey].append( name )
            return ampl_solvers
        return None

#===============================================================================#

    def BuildXmlStringAmpl( self, category, solver, *args ):
        """
        Retrieves the XML template for problem submission to the solver
        specified. This method is particular to solvers accepting AMPL input.
        See BuildXmlString for a more general method.

        The trailing arguments are:
            1. the name of the model file (as a string)
            2. the name of the data file (as a string)
            3. the name of the commands file (as a string)
            4. comments, if any (as a string)
        The 'comments' string can contain line feeds and special characters.
        If, e.g., your model uses no data file, use the empty string instead.
    
        Example: 
          BuildXmlStringAmpl( 'nco',
                              'SNOPT',
                              'mymodel.mod',
                              'mymodel.dat',
                              'mymodel.ampl',
                              'This is a set of uh...\nwitty comments...' )
        """
        if not self.connected:
            return None
        solver_tmplt = self.server.getSolverTemplate(category,solver,'AMPL')
        xmlbits = solver_tmplt.split( '...Insert Value Here...' )
        
        if len(xmlbits) <= 1:
            raise ValueError, "Please check the category:solver:input combo"
            return None
            
        if len(xmlbits) != len(args) + 1:
            sys.stderr.write( 'Insufficient input\n' )
            sys.stderr.write( 'Need %-d arguments, %-d were supplied\n' % (len(xmlbits)-1, len(args) ) )
            return None
        xmlstring = xmlbits[0]
        for i in range( len(args) ):
            if args[i] is not None:
                try:
                    f = open( args[i], 'r' )
                    buffer=1
                    while buffer:
                        buffer =  f.read()
                        xmlstring += buffer
                    f.close()
                except:
                    xmlstring += args[i]
            xmlstring += xmlbits[i+1]
        return xmlstring

#===============================================================================#

    def BuildXmlString( self, category, solver, input, *args ):
        """
        Retrieves the XML template for problem submission to the solver
        specified. The 'input' argument takes one of the values returned by the
        GetInputFormats method. The trailing arguments depend on the input
        format. For specific information, see the corresponding method:
            BuildXmlString[Format]
        (BuildXmlStringAmpl, BuildXmlStringGams, etc.)
        """
        if not self.connected:
            return None
        if input == 'AMPL':
            return self.BuildXmlStringAmpl( category, solver, *args )
        else:
            sys.stderr.write( 'Cannot yet build string for %-s input\n' % input )
            return None

#===============================================================================#

    def SubmitJob( self, xml, **kwargs ):
        if not self.connected:
            return None
        jobid, pwd = self.server.submitJob( xml, **kwargs )
        if jobid == 0:
            raise RuntimeError, pwd
            return None
        offset=0
        status = ''
        while status != "Done":
            #(msg,offset) = self.server.getIntermediateResults(jobid,pwd,offset)
            #sys.stdout.write(msg.data)
            status = self.server.getJobStatus(jobid,pwd)

        msg = self.server.getFinalResults(jobid,pwd).data
        #sys.stdout.write(msg)
        #return (jobid, pwd)
        return msg

#===============================================================================#

    def HelpCallback( self, option, opt_str, value, parser, *args, **kwargs ):
        
        import sys
    
        # General callback for --help command-line options
        if opt_str == '--help-server':
            sys.stderr.write( self.server.emailHelp() )
            sys.exit(0)
        elif opt_str == '--help-methods':
            server_methods = self.GetServerMethods()
            self.PrintDictionary( server_methods )
            sys.exit(0)
        elif opt_str == '--queue':
            sys.stderr.write( self.server.printQueue() )
            sys.exit(0)
        elif opt_str == '--solvers-list':
            solvers_list = self.GetAmplSolvers()
            self.PrintDictionary( solvers_list )
            sys.exit(0)
        return
        

#===============================================================================#
#===============================================================================#

if __name__ == '__main__':

    neos = NeosInterface()
    itson = neos.Connected()
    if not itson:
        sys.stderr.write( 'Either we are currently not connected or\n' )
        sys.stderr.write( 'Neos Server does not appear to be alive\n' )
    else:
        sys.stderr.write( ' Version : %-s' % neos.version + '\n' )

    from optparse import OptionParser

    # Define allowed command-line options
    parser = OptionParser()

    # File name options
    parser.add_option( "-m", "--model", action="store", type="string", dest="modfile",
                       help="Specify AMPL model file" )
    parser.add_option( "-d", "--data",     action="store", type="string", dest="datfile",
                       help="Specify AMPL data file" )
    parser.add_option( "-c", "--commands", action="store", type="string", dest="comfile",
                       help="Specify optional AMPL commands file" )
    parser.add_option( "-k", "--category", action="store", type="string", dest="categ",
                       help="Specify solver category" )
    parser.add_option( "-s", "--solver",   action="store", type="string", dest="solver",
                       help="Specify solver to use" )
    parser.add_option( "-C", "--comment", action="store", type="string", dest="comment",
                       help="Specify comments as a string" )
    
    # Help options
    parser.add_option( "--help-server",  action="callback", callback=neos.HelpCallback,
                       help="Display help message from server" )
    parser.add_option( "--help-methods", action="callback", callback=neos.HelpCallback,
                       help="Display list of methods exported by server" )
    parser.add_option( "--queue",        action="callback", callback=neos.HelpCallback,
                       help="Display current queue" )
    parser.add_option( "--solvers-list", action="callback", callback=neos.HelpCallback,
                       help="Display list of available solvers" )

    # Parse command-line options
    (options, args) = parser.parse_args()

    print ' modfile = ', options.modfile
    print ' datfile = ', options.datfile
    print ' comfile = ', options.comfile
    print ' solver  = ', options.solver
    print ' categ   = ', options.categ
    print ' comment = ', str(options.comment)

    # Check that necessary arguments were given
    if options.modfile is None:
        sys.stderr.write( "Please specify a model file\n" )
        sys.exit( 1 )

    if options.categ is None:
        sys.stderr.write( "Please specify solver category\n" )
        sys.exit( 1 )

    if options.solver is None: 
        sys.stderr.write( "Please specify a solver\n" )
        sys.exit( 1 )

    if options.datfile is None:
        sys.stderr.write( "It would be good usage to have model and data\n" )
        sys.stderr.write( "in two different files. I will forward your model\n" )
        sys.stderr.write( "to the server as-is anyways...\n" )

    # If all looks right, forward model to server
    xml = neos.BuildXmlString( options.categ,
                               options.solver,
                               'AMPL',
                               options.modfile,
                               options.datfile,
                               options.comfile,
                               str(options.comment) )

    #print neos.BuildXmlString( 'nco',
    #                           'SNOPT',
    #                           'AMPL',
    #                           'mymodel.mod',
    #                           'mymodel.dat',
    #                           'mymodel.ampl',
    #                           'This is a set of uh...\nwitty comments...' )

    #xml = neos.BuildXmlString( 'lp',
    #                           'PCx',
    #                           'AMPL',
    #                           'diet1.mod',
    #                           'diet1.dat',\
    #                           'solve;\ndisplay Total_Cost;\ndisplay Buy;',
    #                           None )

    #print xml

    msg = neos.SubmitJob( xml )
    sys.stdout.write( msg )
                                      
#===============================================================================#