#!/usr/bin/env python
import os

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SkittleTree.settings")

    from migrateDB import *

    #RunMigration1()
    #RunMigration2()
    #RunMigration3()
    #RunMigration4()
    #RunMigration5()
    #RunMigration6()
    #RunMigration7()
    #RunMigration8()
    RunMigration9()