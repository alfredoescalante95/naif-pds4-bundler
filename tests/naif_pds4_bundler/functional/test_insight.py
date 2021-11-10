"""Functional Test Family for InSight Archive Generation."""
import glob
import os
import shutil
import unittest
import spiceypy

from unittest import TestCase
from naif_pds4_bundler.__main__ import main
from xmlschema.validators.exceptions import XMLSchemaChildrenValidationError


class TestINSIGHT(TestCase):
    """Functional Test Family Class for InSight Archive Generation."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.

        Clears up the functional tests directory.
        """
        print(f"NPB - Functional Tests - {cls.__name__}")

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        cls.silent = True
        cls.log = True

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

        os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

        dirs = ["working", "staging", "insight", "kernels"]
        for dir in dirs:
            shutil.rmtree(dir, ignore_errors=True)

        if os.path.exists("staging"):
            os.remove("staging")

    def test_insight_basic(self):
        """Test for basic execution of the pipeline.

        Test complete pipeline with basic Insight data: FKs, IKs and a SCLK.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_26.plan"
        faucet = "bundle"

        os.makedirs("working", mode=0o777, exist_ok=True)
        os.makedirs("staging", mode=0o777, exist_ok=True)
        shutil.copy2(
            "../data/insight_release_basic.kernel_list",
            "working/insight_release_07.kernel_list",
        )
        shutil.rmtree("insight", ignore_errors=True)
        shutil.copytree("../data/insight", "insight")
        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree("../data/kernels", "kernels")

        with open("../data/insight.list", "r") as i:
            for line in i:
                with open(f"insight/insight_spice/{line[0:-1]}", "w"):
                    pass

        main(config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_diff_previous_none(self):
        """Test for Diff Files compared with default files.

        Testcase in which products should be compared with previous increment
        of the archive. The reporting of diff files is set to none.
        The pipeline stops before copying the previous increment files
        to the staging area.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")
        shutil.copytree("../data/insight", "insight")

        main(config, plan, faucet, silent=self.silent, log=self.log, diff="")

    def test_insight_diff_previous_all(self):
        """Test for Diff Files compared with previous archive version (1).

        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area. Diffs are reported both in the log and in
        files.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")
        shutil.copytree("../data/insight", "insight")

        main(config, plan, faucet, silent=self.silent, log=self.log, diff="all")

    def test_insight_diff_previous_files(self):
        """Test for Diff Files compared with previous archive version (2).

        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area. Diffs are reported only in files.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")
        shutil.copytree("../data/insight", "insight")

        main(config, plan, faucet, silent=self.silent, log=self.log, diff="files")

    def test_insight_diff_previous_log(self):
        """Test for Diff Files compared with previous archive version (3).

        Testcase in which products are compared with previous increment of the
        archive. The pipeline stops before copying the previous increment
        files to the staging area. Diffs are reported only in log.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")
        shutil.copytree("../data/insight", "insight")

        main(config, plan, faucet, silent=self.silent, log=self.log, diff="log")

    def test_insight_diff_templates(self):
        """Test for Diff Files compared with templates.

        Testcase in which products are compared with the templates to
        generate the products and to similar kernels; the ``bundle_directory``
        files are not present. The pipeline stops before copying the
        previous increment files to the staging area.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        os.makedirs("insight/insight_spice/spice_kernels/sclk", mode=0o777)
        shutil.copy2(
            "../data/insight/insight_spice/spice_kernels/sclk/marcob_fake_v01.xml",
            "insight/insight_spice/spice_kernels/sclk",
        )
        with open(
            "insight/insight_spice/spice_kernels/sclk/marcob_fake_v01.tsc", "w"
        ):
            pass

        main(config, plan, faucet, silent=self.silent, log=self.log, diff="all")

    def test_insight_files_in_staging(self):
        """Test for products present in staging directory.

        Testcase in which products are already present in the staging
        directory. The log provides error messages but the process is not
        stopped. Process is finished before moving all files to the final
        area.

        The tests also tests the obtaining of checksums from already existing
        labels.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")
        shutil.copytree("../data/insight", "staging")

        #
        # The files that are added on top of the staging area need to have
        # their coverage extracted. Those are the files provided in the
        # insight_08.list.
        #
        with open("../data/insight.list", "r") as i:
            for line in i:
                with open(f"staging/insight_spice/{line[0:-1]}", "w"):
                    pass

        shutil.copy2(
            "../data/kernels/sclk/NSY_SCLKSCET.00019.tsc",
            "staging/insight_spice/spice_kernels/sclk/nsy_sclkscet_00019.tsc",
        )

        shutil.copy2(
            "../data/kernels/ck/insight_ida_enc_200829_201220_v1.bc",
            "staging/insight_spice/spice_kernels/ck/",
        )
        shutil.copy2(
            "../data/kernels/ck/insight_ida_enc_200829_201220_v1.xml",
            "staging/insight_spice/spice_kernels/ck/",
        )

        shutil.copy2(
            "../data/kernels/ck/insight_ida_pot_200829_201220_v1.bc",
            "staging/insight_spice/spice_kernels/ck/",
        )
        shutil.copy2(
            "../data/kernels/ck/insight_ida_pot_200829_201220_v1.xml",
            "staging/insight_spice/spice_kernels/ck/",
        )

        shutil.copy2(
            "../data/kernels/mk/insight_v08.tm",
            "staging/insight_spice/spice_kernels/mk/",
        )

        os.makedirs("insight", mode=0o777)

        main(config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_previous_spiceds(self):
        """Test SPICEDS from previous release.

        Testcase for when the SPICEDS file is not provided
        via configuration but the previous version is available.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777, exist_ok=True)
        os.makedirs("working", mode=0o777, exist_ok=True)
        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree(
            "../data/kernels",
            "kernels",
        )
        shutil.copytree("../data/insight", "insight")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spiceds>../data/spiceds_test.html</spiceds>" in line:
                        n.write("        <spiceds> </spiceds>\n")
                    else:
                        n.write(line)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, diff="all")

    def test_insight_start_finish(self):
        """Test Archive increment start and finish times from configuration.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)

        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/insight", "insight")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "</readme>" in line:
                        n.write(
                            "</readme>\n"
                            "<release_date>2021-04-04</release_date>\n"
                            "<increment_start>2021-04-03T20:53:00Z"
                            "</increment_start>\n"
                            "<increment_finish>"
                            "2021-04-23T20:53:00Z</increment_finish>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, diff="")

    def test_insight_incorrect_times(self):
        """Test for incorrect increment start and finish times via configuration.

        Test is successful if NPB raises run time errors for each NPB call.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/insight", "insight")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<mission_start>2018-05-05T11:05:00Z</mission_start>" in line:
                        n.write(
                            "        "
                            "<mission_start>2018-05-05T11:05:00"
                            "</mission_start>\n"
                        )
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(
                updated_config, plan, faucet, silent=self.silent, log=self.log, diff=""
            )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "</readme>" in line:
                        n.write(
                            "        </readme>\n"
                            "        <release_date>2021</release_date>\n"
                        )
                    else:
                        n.write(line)

        with self.assertRaises(RuntimeError):
            main(
                updated_config, plan, faucet, silent=self.silent, log=self.log, diff=""
            )

    def test_insight_mk_input(self):
        """Test incorrect input MK information.

        The MK configuration includes indications of how the INSIGHT MK should
        be named, and even if the kernel is provided manually, NPB still checks
        the expected name and raises an error.

        Test is successful if first run with ``insight_2021_v08.tm`` signals
        this run time error::
           RuntimeError: Meta-kernel insight_2021_v08.tm has not been matched in configuration.

        and then NPB executes without errors with `insight_v08.tm``
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "working/insight.plan"
        faucet = "staging"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        os.makedirs("insight", mode=0o777)

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "        <coverage_kernels>" in line:
                        n.write(
                            "        <mk_inputs>\n"
                            "            <file>working/insight_2021_v08.tm"
                            "</file>\n"
                            "        </mk_inputs>\n"
                            "        <coverage_kernels>\n"
                        )
                    else:
                        n.write(line)

        with open("working/insight_2021_v08.tm", "w") as p:
            p.write("test")

        with open("working/insight.plan", "w") as p:
            p.write("nsy_sclkscet_00019.tsc")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        with self.assertRaises(RuntimeError):
            main(
                updated_config,
                plan,
                faucet,
                silent=self.silent,
                log=self.log,
                diff="all",
            )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<file> </file>" in line:
                        n.write("            <file>../data/insight_v08.tm" "</file>\n")
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log, diff="all")

    def test_insight_mks_input(self):
        """Test MKs with incorrect file architecture.

        A MKs has the appropriate architecture if its first line is::
           KPL/MK

        The test is successful if the following error is raised::
           spiceypy.utils.exceptions.SpiceFILEREADFAILED:
           ================================================================================

           Toolkit version: CSPICE66

           SPICE(FILEREADFAILED) --
           An Attempt to Read a File Failed
           Attempt to read from file 'working/insight_v08.tm' failed. IOSTAT = -1.

           getfat_c --> GETFAT

           ================================================================================
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "working/insight.plan"
        faucet = "staging"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)
        shutil.copytree("../data/kernels", "kernels")
        os.makedirs("insight", mode=0o777)

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "        <coverage_kernels>" in line:
                        n.write(
                            "        <mk_inputs>\n"
                            "<file>working/insight_v08.tm</file>\n"
                            "<file>working/insight_v09.tm</file>\n"
                            "        </mk_inputs>\n"
                            "        <coverage_kernels>\n"
                        )
                    else:
                        n.write(line)

        with open("working/insight_v08.tm", "w") as p:
            p.write("test")
        with open("working/insight_v09.tm", "w") as p:
            p.write("test")

        with open("working/insight.plan", "w") as p:
            p.write("nsy_sclkscet_00019.tsc")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        with self.assertRaises(spiceypy.utils.exceptions.SpiceFILEREADFAILED):
            main(
                updated_config,
                plan,
                faucet,
                silent=self.silent,
                log=self.log,
                diff="all",
            )

    def test_insight_mks_inputs_coverage(self):
        """Test MK coverage not determined from kernels in MK.

        Testcase for when one of the meta-kernels does not include the SPK/CK
        that determines the coverage of the meta-kernel (implemented after
        M2020 Chronos meta-kernel generation.).

        NPB log provides the following message::
           WARNING : -- No kernel(s) found to determine meta-kernel coverage. Mission times will be used:
           WARNING :    2018-05-05T11:05:00Z - 2050-01-01T00:00:00Z

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_00.plan"
        faucet = "bundle"

        dirs = ["working", "staging", "insight"]
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        shutil.copy2(
            "../data/insight_release_basic.kernel_list",
            "working/insight_release_07.kernel_list",
        )
        shutil.rmtree("insight")
        shutil.copytree("../data/insight", "insight")
        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree("../data/kernels", "kernels")
        os.remove("kernels/mk/insight_v08.tm")
        shutil.copy2("../data/insight_v00.tm", "working/insight_v00.tm")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "        <coverage_kernels>" in line:
                        n.write(
                            "        <mk_inputs>\n"
                            "<file>working/insight_v00.tm</file>\n"
                            "        </mk_inputs>\n"
                            "        <coverage_kernels>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_mks_coverage_in_final(self):
        """Test MK coverage determined by kernel in ``bundle_directory``.

        Test MK coverage determination from kernel in MK but not present in
        the current release. NPB will report it in the log as follows::

           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/spk/insight_cru_ops_v1.bsp.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/spk/insight_edl_rec_v1.bsp.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_180505_181127_v1.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_181127_190331_v2.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_190331_190629_v2.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_190629_190918_v2.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_190925_190929_v1.bc.
           WARNING :    It will not be used to determine the coverage.
           INFO    : -- File insight_ida_enc_190929_191120_v1.bc used to determine coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_191120_200321_v1.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_200321_200623_v1.bc.
           WARNING :    It will not be used to determine the coverage.
           WARNING : -- File not present in final area: /insight/insight_spice/spice_kernels/ck/insight_ida_enc_200623_200829_v1.bc.
           WARNING :    It will not be used to determine the coverage.
           INFO    : -- Meta-kernel coverage: 2019-11-07T02:00:00Z - 2020-11-07T03:00:00Z

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_00.plan"
        faucet = "bundle"

        dirs = ["working", "staging", "insight"]
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        shutil.copy2(
            "../data/insight_release_basic.kernel_list",
            "working/insight_release_07.kernel_list",
        )
        shutil.rmtree("insight")
        shutil.copytree("../data/insight", "insight")
        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree("../data/kernels", "kernels")
        shutil.copy2("../data/insight_v08.tm", "working/insight_v08.tm")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "        <coverage_kernels>" in line:
                        n.write(
                            "        <mk_inputs>\n"
                            "<file>working/insight_v08.tm</file>\n"
                            "        </mk_inputs>\n"
                            "        <coverage_kernels>\n"
                        )
                    else:
                        n.write(line)

        main(updated_config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_generate_mk(self):
        """Test MK generation with no MK input.

        Test is successful if NPB is executed without errors.
        """
        dirs = ["working", "staging", "insight"]
        for dir in dirs:
            os.makedirs(dir, 0o766, exist_ok=True)

        shutil.rmtree("kernels", ignore_errors=True)
        shutil.copytree("../data/kernels", "kernels")

        config = "../config/insight.xml"
        plan = "working/insight.plan"
        faucet = "staging"

        with open(plan, "w") as p:
            p.write("nsy_sclkscet_00019.tsc")

        main(
                config,
                plan=plan,
                faucet=faucet,
                silent=self.silent,
                log=self.log
            )

    def test_insight_no_spiceds_in_conf(self):
        """Test when no SPICEDS is provided via configuration.

        Testcase for when the SPICEDS file is not provided
        via configuration but the previous version is available.
        The WARNING message provided by the NPB log is as follows::

           INFO    : -- No spiceds file provided.
           INFO    : -- Previous spiceds found: /insight/insight_spice/document/spiceds_v001.html

        The first call to NPB is done with a configuration file with the
        ``<spiceds>`` element whereas the second one does not.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        shutil.copytree("../data/kernels", "kernels")
        shutil.copytree("../data/insight", "insight")

        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spiceds>../data/spiceds_insight.html</spiceds>" in line:
                        n.write("        <spiceds></spiceds>\n")
                    else:
                        n.write(line)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        main(
            updated_config,
            plan,
            faucet,
            silent=self.silent,
            log=self.log
        )

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spiceds>../data/spiceds_insight.html</spiceds>" in line:
                        n.write("")
                    else:
                        n.write(line)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        main(
            updated_config,
            plan,
            faucet,
            silent=self.silent,
            log=self.log,
            diff="all",
        )

    def test_insight_no_spiceds(self):
        """Test when no SPICEDS is available.

        Testcase for when the SPICEDS file is not provided
        via configuration and the previous version is not available.

        The test is successful if the following error is raised::
           RuntimeError: spiceds not provided and not available from previous releases.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "staging"

        shutil.copytree("../data/kernels", "kernels")

        os.makedirs("insight", mode=0o777)
        os.makedirs("staging", mode=0o777)
        os.makedirs("working", mode=0o777)
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spiceds>../data/spiceds_insight.html</spiceds>" in line:
                        n.write("        <spiceds></spiceds>\n")
                    else:
                        n.write(line)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        with self.assertRaises(RuntimeError):
            main(
                updated_config,
                plan,
                faucet,
                silent=self.silent,
                log=self.log
            )

    def test_insight_no_readme(self):
        """Test when the readme file is not present.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)

        shutil.copytree("../data/kernels", "kernels")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        os.makedirs("insight")

        main(config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_no_readme_in_config(self):
        """Test when the readme file is not provided via configuration.

        The first run raises an the following error::
           RuntimeError: readme file not present in configuration.

        because the readme file is not present in the ``bundle_directory``.
        The second run includes the readme file in the bundle directory and
        therefore it does not raise an error.

        The test is successful if the conditions specified above are met.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)

        shutil.copytree("../data/kernels", "kernels")

        os.makedirs("insight")

        write_config = True
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<readme>" in line:
                        write_config = False
                    if write_config:
                        n.write(line)
                    if "</readme>" in line:
                        write_config = True

        with self.assertRaises(RuntimeError):
            main(updated_config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_readme_incomplete_in_config(self):
        """Test when the readme file configuration is not complete.

        The error is detected by the XML validation against the schema.

         The test is successful if the following error is raised::
            Reason: The content of element 'readme' is not complete. Tag 'cognisant_authority' expected.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        plan = "../data/insight_release_08.plan"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)

        shutil.copytree("../data/kernels", "kernels")

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        os.makedirs("insight")

        write_config = True
        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<cognisant_authority>" in line:
                        write_config = False
                    if write_config:
                        n.write(line)
                    if "</cognisant_authority>" in line:
                        write_config = True

        with self.assertRaises(KeyError):
            main(updated_config, plan, faucet, silent=self.silent, log=self.log)

    def test_insight_no_kernels(self):
        """Test without bundle and no input kernels provided but a SPICEDS is.

        NPB log will include the following WARNING message::
           WARNING : -- No kernels will be added to the increment.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)
        os.makedirs("kernels", mode=0o777)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        os.makedirs("insight")

        main(
            config,
            plan=False,
            faucet=faucet,
            silent=self.silent,
            log=self.log
        )

    def test_insight_no_kernels_with_bundle(self):
        """Test without input kernels provided but a SPICEDS is.

        NPB log will include the following WARNING message::
           WARNING : -- No kernels will be added to the increment.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)
        os.makedirs("kernels", mode=0o777)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        shutil.copytree("../data/insight", "insight")

        main(
            config,
            plan=False,
            faucet=faucet,
            silent=self.silent,
            log=self.log
        )

    def test_insight_only_cheksums(self):
        """Test without any input (kernels or SPICEDS).

        No inputs are provided at all but checksums are generated.

        Test is successful if NPB is executed without errors.
        """
        config = "../config/insight.xml"
        updated_config = "working/insight.xml"
        faucet = "bundle"

        os.makedirs("working", mode=0o777)
        os.makedirs("staging", mode=0o777)
        os.makedirs("kernels", mode=0o777)

        for file in glob.glob("../data/insight_release_0[0-7].kernel_list"):
            shutil.copy2(file, "working")

        shutil.copytree("../data/insight", "insight")

        with open(config, "r") as c:
            with open(updated_config, "w") as n:
                for line in c:
                    if "<spiceds>../data/spiceds_insight.html</spiceds>" in line:
                        n.write("            " "<spiceds> </spiceds>\n")
                    else:
                        n.write(line)

        main(
            updated_config,
            plan=False,
            faucet=faucet,
            silent=self.silent,
            log=self.log
        )


if __name__ == "__main__":
    unittest.main()
