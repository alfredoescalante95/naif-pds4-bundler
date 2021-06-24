import os
import re
import glob
import logging
import spiceypy
import datetime
import xmlschema
from pathlib import Path
from os.path import dirname
from xml.etree import cElementTree as ET
from npb.utils.files import etree_to_dict
from npb.classes.log import error_message


class Setup(object):
    """
    Class that parses and processes the NPB XML configuration file
    and makes it available to all other classes.

    :param args: Parameters arguments from NPB's main function.
    :param version: NPB version.
    """

    def __init__(self, args, version):
        """
        Constructor method.
        """
        #
        # Check that the configuration file validates with its schema
        #
        try:
            schema = xmlschema.XMLSchema11(dirname(__file__) + 
                                           '/../templates/configuration.xsd')
            schema.validate(args.config)
            
        except Exception as inst:
            print(inst)
            
        
        #
        # Converting XML setup file into a dictionary and then into
        # attributes for the object.
        #
        config = Path(args.config).read_text()
        entries = etree_to_dict(ET.XML(config))

        #
        # Re-arrange the resulting dictionary into one-level attributes
        # adept to be used (as if we were loading a JSON file).
        #
        config = entries['naif-pds4-bundle_configuration']

        self.__dict__.update(config['pds_parameters'])
        self.__dict__.update(config['bundle_parameters'])
        self.__dict__.update(config['mission_parameters'])
        self.__dict__.update(config['directories'])

        #
        # Kernel list configuration needs refractoring.
        #
        self.__dict__.update(config['kernel_list'])

        kernel_list_config = {}
        for ker in self.kernel:
            kernel_list_config[ker['@pattern']] = ker

        self.kernel_list_config = kernel_list_config
        del self.kernel

        #
        # Meta-kernel configuration; if there is one meta-kernel
        # mk is a dictionary, otherwise it is a list of dictionaries.
        # It is processed in such a way that it is always a list of
        # dictionaries. Same applies to meta-kernels from configutarion
        # as user input.
        #
        self.__dict__.update(config['meta-kernel'])
        if hasattr(self, 'mk'):
            if isinstance(self.mk, dict):
                self.mk = [self.mk]
        if hasattr(self, 'mk_inputs'):
            if isinstance(self.mk_inputs, dict):
                self.mk_inputs = [self.mk_inputs]

        #
        # Orbnum configuration: if there is one orbnum file orbnum is a
        # dictionary, otherwise it is a list of dictionaries. It is
        # processed in such a way that it is always a list of dictionaries
        #
        if 'orbit_number_file' in config:
            self.__dict__.update(config['orbit_number_file'])
            if isinstance(self.orbnum, dict):
                self.orbnum = [self.orbnum]

        #
        # Populate the setup object with attributes not present in the
        # configuration file.
        #
        self.root_dir = os.path.dirname(__file__)[:-7]
        self.step = 1
        self.version = version
        self.args = args
        self.interactive = args.interactive
        self.faucet = args.faucet.lower()
        self.diff = args.diff.lower()
        self.today = datetime.date.today().strftime("%Y%m%d")

        #
        # If a release date is not specified it is set to today.
        #
        if not hasattr(self, 'release_date'):
            self.release_date = datetime.date.today().strftime("%Y-%m-%d")
        else:
            pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
            if not pattern.match(self.release_date):
                error_message('release_date parameter does not match '
                              'the required format: YYYY-MM-DD.')

        #
        # Determination of the templates used.
        #
        if hasattr(self, 'templates_directory'):
            self.templates_directory = \
                f'{self.root_dir}templates/{self.information_model}'

        #
        # Check date format, if is not provided it is set to the format
        # proposed for the PDS4 Information Model 2.0.
        #
        if not hasattr(self, 'date_format'):
            self.date_format = 'infomod2'

        #
        # Check End of Line format and set EoL length.
        #
        if self.end_of_line == 'CRLF':
            self.eol = '\r\n'
            self.eol_len = 2
        elif self.end_of_line == 'LF':
            self.eol = '\n'
            self.eol_len = 1
        else:
            error_message('End of Line provided via configuration is not '
                          'CRLF nor LF')

        #
        # Fill PDS4 missing fields.
        #
        if self.pds_version == '4':
            self.producer_phone = ''
            self.producer_email = ''
            self.dataset_id = ''
            self.volume_id = ''

    def check_configuration(self):
        """
        Performs a number of checks on some of the loaded configuration
        items.
        """
        #
        # Check Bundle increment start and finish times. For the two accepted
        # formats
        #
        if self.date_format == 'infomod2':
        
            pattern = re.compile(
                    '[0-9]{4}-[0-9]{2}-[0-9]{2}T'
                    '[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}Z')
            format = 'YYYY-MM-DDThh:mm:ss.sssZ'
        elif self.date_format == 'makelbl':
            
            pattern = re.compile(
                    '[0-9]{4}-[0-9]{2}-[0-9]{2}T'
                    '[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
            format = 'YYYY-MM-DDThh:mm:ssZ'
        else:
            error_message('date_format parameter is not infomod2 or makelbl.')
            
        if hasattr(self, 'mission_start') and self.mission_start:
            if not pattern.match(self.mission_start):
                error_message(f'mission_start parameter does not match the '
                              f'required format: {format}.')
        if hasattr(self, 'mission_finish') and self.mission_finish:
            if not pattern.match(self.mission_finish):
                error_message(f'mission_finish does not match the required '
                              f'format: {format}.')
        if hasattr(self, 'increment_start') and self.increment_start:
            if not pattern.match(self.increment_start):
                error_message(f'increment_start parameter does not match the '
                              f'required format: {format}.')
        if hasattr(self, 'increment_finish') and self.increment_finish:
            if not pattern.match(self.increment_finish):
                error_message(f'increment_finish does not match the required '
                              f'format: {format}.')
        if hasattr(self, 'increment_start') and \
                hasattr(self, 'increment_finish'):
            if ((not self.increment_start) and (self.increment_finish)) or (
                    (self.increment_start) and (not self.increment_finish)):
                error_message(
                    'If provided via configuration, increment_start and '
                    'increment_finish parameters need to be provided '
                    'together.')

        #
        # Sort out if directories are provided as relative paths and
        # if so convert them in absolute for the execution
        #
        cwd = os.getcwd()

        os.chdir('/')

        if os.path.isdir(cwd + os.sep + self.working_directory):
            self.working_directory = cwd + os.sep + self.working_directory
        if not os.path.isdir(self.working_directory):
            error_message(f'Directory does not exist: '
                          f'{self.working_directory}')

        if os.path.isdir(cwd + os.sep + self.staging_directory):
            self.staging_directory = cwd + os.sep + self.staging_directory + \
                                     f'/{self.mission_accronym}_spice'
        elif not os.path.isdir(self.staging_directory):
            print(f'Creating missing directory: {self.staging_directory}/'
                  f'{self.mission_accronym}_spice')
            try:
                os.mkdir(self.staging_directory)
            except Exception as e:
                print(e)
        elif f'/{self.mission_accronym}_spice' not in self.staging_directory:
            self.staging_directory += f'/{self.mission_accronym}_spice'

        if os.path.isdir(cwd + os.sep + self.final_directory):
            self.final_directory = cwd + os.sep + self.final_directory
        if not os.path.isdir(self.final_directory):
            error_message(f'Directory does not exist: '
                          f'{self.final_directory}')

        if os.path.isdir(cwd + os.sep + self.kernels_directory):
            self.kernels_directory = cwd + os.sep + self.kernels_directory
        if not os.path.isdir(self.kernels_directory):
            error_message(f'Directory does not exist: '
                          f'{self.kernels_directory}')

        os.chdir(cwd)

        #
        # Check existence of templates according to the information_model
        # or user-defined templates.
        #
        if not hasattr(self, 'templates_directory') and \
                self.pds_version == "4":

            config_schema = self.information_model.split('.')
            config_schema = float(f'{int(config_schema[0]):03d}'
                                  f'{int(config_schema[1]):03d}'
                                  f'{int(config_schema[2]):03d}'
                                  f'{int(config_schema[3]):03d}')

            schemas = [os.path.basename(x[:-1]) for x in
                       glob.glob(f'{self.root_dir}templates/*/')]

            schemas_eval = []
            for schema in schemas:
                schema = schema.split('.')
                schema = float(f'{int(schema[0]):03d}'
                               f'{int(schema[1]):03d}'
                               f'{int(schema[2]):03d}'
                               f'{int(schema[3]):03d}')
                schemas_eval.append(schema)

            schemas_eval = sorted(schemas_eval)

            i = 0
            while i < len(schemas_eval):
                if config_schema < schemas_eval[i]:
                    try:
                        schema = schemas[i - 1]
                    except:
                        schema = schemas[0]
                    break
                if config_schema > schemas_eval[i]:
                    schema = schemas[i]
                    break
                i += 1

            self.templates_directory = f'{self.root_dir}/templates/{schema}/'

            logging.warning(f'-- Label templates will use the ones from '
                            f'information model {schema}.')
            logging.warning('')
        elif self.pds_version == '4':
            if not os.path.isdir(self.templates_directory):
                error_message('Path provided/derived for templates '
                                'is not available')
            labels_check = [os.path.basename(x[:-1]) for x in
                            glob.glob(f'{self.root_dir}templates/1.5.0.0/*')]
            labels = [os.path.basename(x[:-1]) for x in
                      glob.glob(f'{self.templates_directory}/*')]
            for label in labels_check:
                if label not in labels:
                    error_message(f'Template {label} has not been provided.')

        #
        # Check meta-kernel configuration
        #
        if hasattr(self, 'mk'):
            for metak in self.mk:

                #
                # Turn all name_patterns to lists.
                #
                if not isinstance(metak['name'], list):
                    metak['name_patterns'] = list(metak['name'])

                metal_name_check = metak['@name']

                #
                # Fix no list or list of lists.
                #
                patterns_dict = metak['name']['pattern']
                if not isinstance(patterns_dict, list):
                    patterns = []
                    dictionary_copy = patterns_dict.copy()
                    patterns.append(dictionary_copy)
                else:
                    patterns = patterns_dict

                for pattern in patterns:
                    name_pattern = pattern['#text']
                    if not name_pattern in metal_name_check:
                        error_message(f"The meta-kernel pattern "
                                      f"{name_pattern} is not provided")

                    metal_name_check = metal_name_check.replace('$' +
                                                                name_pattern,
                                                                '')

                #
                # If there are remmaining $ characters in the metal_name_check
                # this means that there are remaining patterns to define in
                # the configuration file.
                #
                if '$' in metal_name_check:
                    error_message(f'The meta-kernel patterns for are not '
                                  f'defined via configuration')
            else:
                logging.warning('-- There is no meta-kernel configuration '
                                'to check.')

        #
        # Check coverage kernels configuration (needed if there is only one
        # entry).
        #
        if hasattr(self, 'coverage_kernels'):
            if not isinstance(self.coverage_kernels, list):
                self.coverage_kernels = [self.coverage_kernels]

        return None

    def set_release(self):
        """
        Determines the Bundle release number.
        """
        line = f'Step {self.step} - Setup the archive generation'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.step += 1
        if not self.args.silent and not self.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        #
        # PDS4 release increment (implies inventory and meta-kernel).
        #
        logging.info('-- Checking existence of previous release.')

        try:
            releases = glob.glob(self.final_directory + os.sep +
                                 self.mission_accronym + '_spice' + os.sep +
                                 f'bundle_{self.mission_accronym}_spice_v*')
            releases.sort()
            current_release = \
                int(releases[-1].split('_spice_v')[-1].split('.')[0])
            current_release = f'{current_release:03}'
            release = int(current_release) + 1
            release = f'{release:03}'

            logging.info(f'     Generating release {release}.')

            increment = True

        except:
            logging.warning('-- Bundle label not found. Checking previous '
                            'kernel list.')

            try:
                releases = glob.glob(self.working_directory +
                                     f'/{self.mission_accronym}'
                                     f'_release_*.kernel_list')

                releases.sort()
                current_release = int(releases[-1].split(
                    '_release_')[-1].split('.')[0])
                current_release = f'{current_release:03}'
                release = int(current_release) + 1
                release = f'{release:03}'

                logging.info(f'     Generating release {release}')

                increment = True
            except:

                logging.warning('     This is the first release.')

                release = '001'
                current_release = ''

                increment = False

        self.release = release
        self.current_release = current_release

        logging.info('')

        if self.interactive:
            input(">> Press Enter to continue...")

        self.increment = increment

        return None

    def load_kernels(self):
        """
        Loads the kernels required to run NPB. Note that kernels that
        are not required might be loaded as well, but given that the
        required memory is not much, we stay on the safe side by loading
        additional kernels.
        """
        line = f'Step {self.step} - Load LSK, PCK, FK and SCLK kernels'
        logging.info('')
        logging.info(line)
        logging.info('-' * len(line))
        logging.info('')
        self.step += 1
        if not self.args.silent and not self.args.verbose:
            print('-- ' + line.split(' - ')[-1] + '.')

        #
        # To get the appropriate kernels, use the kernel list config.
        # First extract the patterns for each kernel type of interest.
        #
        fk_patterns = []
        sclk_patterns = []
        pck_patterns = []
        lsk_patterns = []

        for type in self.kernels_to_load:
            if 'fk' in type:
                fks = self.kernels_to_load[type]
                if not isinstance(fks, list):
                    fks = [fks]
                for fk in fks:
                    fk_patterns.append(fk)
            elif 'sclk' in type:
                sclks = self.kernels_to_load[type]
                if not isinstance(sclks, list):
                    sclks = [sclks]
                for sclk in sclks:
                    sclk_patterns.append(sclk)
            elif 'pck' in type:
                pcks = self.kernels_to_load[type]
                if not isinstance(pcks, list):
                    pcks = [pcks]
                for pck in pcks:
                    pck_patterns.append(pck)
            elif 'lsk' in type:
                lsks = self.kernels_to_load[type]
                if not isinstance(lsks, list):
                    lsks = [lsks]
                for lsk in lsks:
                    lsk_patterns.append(lsk)

        #
        # Search the latest version for each pattern of each kernel type.
        #
        lsks = []
        for pattern in lsk_patterns:
            if os.path.exists(pattern):
                lsks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                lsk_pattern = [f for f in os.listdir(
                    f'{self.kernels_directory}/lsk/')
                               if re.search(pattern, f)]
                if lsk_pattern:
                    if len(lsk_pattern) > 1: lsk_pattern.sort()
                    lsks.append(lsk_pattern[-1])
                    spiceypy.furnsh(f'{self.kernels_directory}/lsk/'
                                    f'{lsk_pattern[-1]}')
        if not lsk:
            logging.error(f'-- LSK not found.')
        else:
            logging.info(f'-- LSK     loaded: {lsks}')
        if len(lsks) > 1:
            error_message('Only one LSK should be obtained.')

        pcks = []
        for pattern in pck_patterns:
            if os.path.exists(pattern):
                pcks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                pcks_pattern = [f for f in os.listdir(
                    f'{self.kernels_directory}/pck/') if
                                re.search(pattern, f)]
                if pcks_pattern:
                    if len(pcks_pattern) > 1: pcks_pattern.sort()
                    spiceypy.furnsh(f'{self.kernels_directory}/pck/'
                                    f'{pcks_pattern[-1]}')
                    pcks.append(pcks_pattern[-1])
        if not pcks:
            logging.warning(f'-- PCK not found.')
        else:
            logging.info(f'-- PCK(s)   loaded: {pcks}')

        fks = []
        for pattern in fk_patterns:
            if os.path.exists(pattern):
                fks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                fks_pattern = [f for f in os.listdir(
                    f'{self.kernels_directory}/fk/') if
                               re.search(pattern, f)]
                if fks_pattern:
                    if len(fks_pattern) > 1: fks_pattern.sort()
                    spiceypy.furnsh(f'{self.kernels_directory}/fk/'
                                    f'{fks_pattern[-1]}')
                    fks.append(fks_pattern[-1])
        if not fks:
            logging.warning(f'-- FK not found.')
        else:
            logging.info(f'-- FK(s)   loaded: {fks}')

        sclks = []
        for pattern in sclk_patterns:
            if os.path.exists(pattern):
                sclks.append(pattern)
                spiceypy.furnsh(pattern)
            else:
                sclks_pattern = [f for f in os.listdir(
                    f'{self.kernels_directory}/sclk/') if
                                 re.search(pattern, f)]
                if sclks_pattern:
                    if len(sclks_pattern) > 1: sclks_pattern.sort()
                    sclks.append(sclks_pattern[-1])
                    spiceypy.furnsh(f'{self.kernels_directory}/sclk/'
                                    f'{sclks_pattern[-1]}')
        if not sclks:
            logging.error(f'-- SCLK not found.')
        else:
            logging.info(f'-- SCLK(s) loaded: {sclks}')

        logging.info('')

        self.fks = fks
        self.sclks = sclks
        self.lsk = lsk

        if self.interactive:
            input(">> Press Enter to continue...")

        return None

    def check_times(self):
        """
        Check the correctness of the times provided from the configuration
        file.q
        """
        try:
            et_msn_strt = spiceypy.utc2et(self.mission_start)
            et_inc_strt = spiceypy.utc2et(self.increment_start)
            et_inc_stop = spiceypy.utc2et(self.increment_finish)
            et_mis_stop = spiceypy.utc2et(self.mission_finish)
            logging.info('-- Provided dates are loadable with current setup.')

        except Exception as e:
            logging.error('-- Provided dates are not loadable with current '
                          'setup.')
            error_message(e)

        if not (et_msn_strt < et_inc_strt) or not \
                (et_inc_strt <= et_inc_stop) or not \
                (et_inc_stop <= et_mis_stop) or not \
                (et_msn_strt < et_mis_stop):
            error_message('-- Provided dates are note correct. Check the '
                          'archive coverage')

        return None
