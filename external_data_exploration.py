import pandas as pd
import os
import re


# def external_data_file_overview():
#     files_in_external = os.listdir("Database/External/")

#     overview = []

#     for f in files_in_external:
#         cur_db = pd.read_pickle("Database/External/{0}".format(f))
#         overview.append(
#             pd.DataFrame(
#                 {"file_name": f,
#                  "name": re.sub('.pkl', '', f),
#                  "nrow": cur_db.shape[0],
#                  "col_names": [", ".join(map(str, list(cur_db.columns[1::])))]
#                  }
#             )
#         )
#         print(f, cur_db)

#     overview = pd.concat(overview)
#     overview.reset_index(inplace=True, drop=True)

# # -TODO: this is not automated at all but should be.

#     overview["data_type"] = None
#     overview["note"] = None

#     # manually assigning all the data types. there is just no other way,
#     # it has the highest quality.
#     # this is highly problematic if new columns are added to the database.
#     # and should be changed to a somewhat generic function that
#     # as soon as possible. this is monsterous. careful.

#     type_str = "Nominal"
#     type_int = "Numeric"
#     type_empty = "empty"
#     type_cat = "Ordinal"
#     type_cmplx = "unprocessed Data Structure"
#     type_date = "type_date"

#     overview['data_type'][0] = type_str
#     overview['data_type'][1] = type_str
#     overview['note'][1] = "EMD with # as Seperator"
#     overview['data_type'][2] = type_cat
#     overview['data_type'][3] = type_int
#     overview['data_type'][4] = type_str
#     overview['note'][4] = "could be a category, check number of unique strings"
#     overview['data_type'][5] = type_int
#     overview['data_type'][6] = type_cmplx
#     overview['note'][6] = "Chain of Numbers with # as Seperator"
#     overview['data_type'][7] = type_str
#     overview['data_type'][7] = type_str
#     overview['note'][7] = " Some kind of nested list information with # as seperator"
#     overview['data_type'][8] = type_str
#     overview['note'][8] = "list type_int-codes with # as sep."
#     overview['data_type'][9] = type_cmplx  # type_int-codes with # as sep.
#     overview['note'][9] = "type_int-codes with # as seperator"
#     overview['data_type'][10] = type_cat
#     overview['data_type'][11] = type_str
#     overview['data_type'][12] = type_int
#     overview['data_type'][13] = type_str
#     overview['note'][13] = "List of Authors with , (comma) as Sep."
#     overview['data_type'][14] = type_cat
#     overview['data_type'][15] = type_int
#     overview['data_type'][16] = type_int
#     overview['data_type'][17] = type_int
#     overview['data_type'][18] = type_int
#     overview['data_type'][19] = type_int
#     overview['data_type'][20] = type_int
#     overview['data_type'][21] = type_int
#     overview['data_type'][22] = type_date
#     overview['data_type'][23] = type_int
#     overview['data_type'][24] = type_str
#     overview['data_type'][25] = type_int
#     overview['data_type'][26] = type_str
#     overview['data_type'][27] = type_str
#     overview['note'][27] = "complex data Structure of some kind"
#     overview['data_type'][28] = type_cat
#     overview['data_type'][29] = type_int
#     overview['data_type'][30] = type_cat
#     overview['data_type'][31] = type_empty
#     overview['data_type'][32] = type_empty
#     overview['data_type'][33] = type_empty
#     overview['data_type'][34] = type_int
#     overview['data_type'][35] = type_int
#     overview['data_type'][36] = type_date
#     overview['data_type'][37] = type_str  # details, long text
#     overview['data_type'][38] = type_str
#     overview['data_type'][39] = type_str
#     overview['data_type'][40] = type_str
#     overview['data_type'][41] = type_cat  # bins like in a histogram
#     overview['data_type'][42] = type_str
#     overview['data_type'][43] = type_cat  # embedding yes/no
#     overview['data_type'][44] = type_str  # embedding position
#     overview['data_type'][45] = type_empty
#     overview['data_type'][46] = type_int
#     overview['data_type'][47] = type_int
#     overview['data_type'][48] = type_cat
#     overview['data_type'][49] = type_cat
#     overview['data_type'][50] = type_cat
#     overview['data_type'][51] = type_int
#     overview['data_type'][52] = type_int
#     overview['data_type'][53] = type_str  # hash as some sort of seperator
#     overview['data_type'][54] = type_str
#     overview['data_type'][55] = type_int
#     overview['data_type'][56] = type_cat  # bins..
#     overview['data_type'][57] = type_cmplx
#     overview['data_type'][58] = type_str  # some chain object...
#     overview['data_type'][59] = type_int  # mostly but with some errors in the data.. some type_strs.
#     overview['note'][59] = "mostly type_int but with some errors in the data.. some type_strs."  # mostly but with some errors in the data.. some type_strs.
#     overview['data_type'][60] = type_str
#     overview['data_type'][61] = type_empty
#     overview['data_type'][62] = type_cmplx
#     overview['data_type'][63] = type_str
#     overview['data_type'][64] = type_str
#     overview['data_type'][65] = type_int
#     overview['data_type'][66] = type_int
#     overview['data_type'][67] = type_int
#     overview['data_type'][68] = type_int
#     overview['data_type'][69] = type_str
#     overview['data_type'][70] = type_str
#     overview['data_type'][71] = type_int
#     overview['data_type'][72] = type_str
#     overview['data_type'][73] = type_cmplx
#     overview['data_type'][74] = type_cat
#     overview['data_type'][75] = type_cat
#     overview['data_type'][76] = type_str
#     overview['data_type'][77] = type_cat
#     overview['data_type'][78] = type_cat
#     overview['data_type'][79] = type_cmplx
#     overview['note'][79] = "some kind of chain with # as seperator"
#     overview['data_type'][80] = type_int
#     overview['data_type'][81] = type_empty
#     overview['data_type'][82] = type_empty
#     overview['data_type'][83] = type_str
#     overview['note'][83] = "pdb doi hyperlink"
#     overview['data_type'][84] = type_str
#     overview['data_type'][85] = type_cmplx
#     overview['data_type'][86] = type_str
#     overview['data_type'][87] = type_str
#     overview['data_type'][88] = type_int
#     overview['data_type'][89] = type_int
#     overview['data_type'][90] = type_str
#     overview['data_type'][90] = type_str
#     overview['data_type'][91] = type_str
#     overview['data_type'][92] = type_cat
#     overview['data_type'][93] = type_cat
#     overview['data_type'][94] = type_cat
#     overview['data_type'][95] = type_cat
#     overview['data_type'][96] = type_date
#     overview['data_type'][97] = type_str
#     overview['data_type'][98] = type_int
#     overview['data_type'][99] = type_int
#     overview['data_type'][100] = type_int
#     overview['data_type'][101] = type_int
#     overview['data_type'][102] = type_int
#     overview['data_type'][103] = type_int
#     overview['data_type'][104] = type_int
#     overview['data_type'][105] = type_int
#     overview['data_type'][106] = type_cat
#     overview['data_type'][107] = type_int
#     overview['data_type'][108] = type_int
#     overview['data_type'][109] = type_date
#     overview['data_type'][110] = type_int
#     overview['data_type'][111] = type_int
#     overview['data_type'][112] = type_cmplx
#     overview['note'][112] = "type_date list with # as seperator, probably if revision happend > 1 times"
#     overview['data_type'][113] = type_int
#     overview['data_type'][114] = type_int
#     overview['data_type'][115] = type_int
#     overview['data_type'][116] = type_str
#     overview['data_type'][117] = type_str
#     overview['data_type'][118] = type_cmplx
#     overview['data_type'][119] = type_cat
#     overview['data_type'][120] = type_str
#     overview['note'][120] = "sequence, could be input for some sequence viewer functions or something like that."
#     overview['data_type'][121] = type_cat
#     overview['note'][121] = "ratio between solvents - often H20 vs. D20, sometimes different. Could be split into two columns"
#     overview['data_type'][122] = type_cat
#     overview['note'][122] = "species where protein resides, interesting category for analysis."
#     overview['data_type'][123] = type_cmplx
#     overview['data_type'][124] = type_cat  # yes, no
#     overview['data_type'][125] = type_str
#     overview['data_type'][126] = type_cat
#     overview['data_type'][127] = type_int
#     overview['data_type'][128] = type_str
#     overview['data_type'][129] = type_cat
#     overview['data_type'][130] = type_str
#     overview['data_type'][131] = type_cat
#     overview['data_type'][132] = type_int
#     overview['data_type'][133] = type_int
#     overview['data_type'][134] = type_str
#     overview['data_type'][135] = type_int
#     overview['data_type'][136] = type_int
#     overview['data_type'][137] = type_cat
#     overview['data_type'][138] = type_str
#     overview['data_type'][139] = type_str
#     overview['data_type'][140] = type_str
#     overview['data_type'][141] = type_int
#     overview['data_type'][142] = type_int
#     overview['data_type'][143] = type_int
#     overview['data_type'][144] = type_cmplx
#     overview['data_type'][145] = type_cat
#     overview['data_type'][146] = type_int
#     overview['data_type'][147] = type_int

#     def create_frontend_names(overview):
#         overview["frontend_names"] = None
#         for row in range(overview.shape[0]):
#             overview["frontend_names"][row] = overview.col_names[row] \
#                 + " (" + overview.data_type[row] + ")"
#         return overview

#     overview = create_frontend_names(overview)
#     return overview


def subset_useable_data():
    # not useable:

    # abstractTextShort.pkl
    # additionalMap.pkl

    # # maybe useable
    # authorAssignedEntityName.pkl
    # citationAuthor.pkl
    # clusterNumber100.pkl
    # clusterNumber30.pkl
    # clusterNumber40.pkl
    # clusterNumber50.pkl
    # clusterNumber70.pkl
    # clusterNumber90.pkl
    # clusterNumber95.pkl
    # compound.pkl
    # device.pkl
    # diffractionSource.pkl
    # entityMacromoleculeType.pkl
    # ligandMolecularWeight.pkl # but 9000 samples..

    useable = \
        ["aggregationState.pkl",
         "atomSiteCount.pkl",
         "averageBFactor.pkl",
         "chainLength.pkl",
         "classification.pkl",
         "collectionTemperature.pkl",
         "crystallizationMethod.pkl",
         "crystallizationTempK.pkl",
         "db_name.pkl",
         "densityMatthews.pkl",
         "densityPercentSol.pkl",
         "emResolution.pkl",
         "experimentalTechnique.pkl",
         "expressionHost.pkl",
         "highResolutionLimit.pkl",
         "journalName.pkl",
         # "firstPage.pkl", # broken
         # "lastPage.pkl", # broken
         "lengthOfUnitCellLatticeA.pkl",
         "lengthOfUnitCellLatticeB.pkl",
         "lengthOfUnitCellLatticeC.pkl",
         "macromoleculeType.pkl",
         "molecularWeight.pkl",
         "pdbDoi.pkl",
         "phValue.pkl",
         # "publicationYear.pkl", # broken
         # "pubmedId.pkl", # broken
         "rankNumber100.pkl",
         "rankNumber30.pkl",
         "rankNumber40.pkl",
         "rankNumber50.pkl",
         "rankNumber70.pkl",
         "rankNumber90.pkl",
         "rankNumber95.pkl",
         "clusterNumber100.pkl",
         "clusterNumber30.pkl",
         "clusterNumber40.pkl",  # 1000 - A B C D E ... all the same
         "clusterNumber50.pkl",
         "clusterNumber70.pkl",
         "clusterNumber90.pkl",
         "clusterNumber95.pkl",
         "reconstructionMethod.pkl",
         "refinementResolution.pkl",
         "reflectionsForRefinement.pkl",  # 5000 - A B C D E - each have diff value
         "releaseDate.pkl",
         "residueCount.pkl",
         "resolution.pkl",
         "revisionDate.pkl",
         "rFree.pkl",
         "rObserved.pkl",
         "rWork.pkl",
         "sequence.pkl",
         "source.pkl",
         "structureAuthor.pkl",
         "structureDeterminationMethod.pkl",
         "structureMolecularWeight.pkl",
         "structureTitle.pkl",
         "taxonomy.pkl",
         # "title.pkl", #title
         "unitCellAngleAlpha.pkl",
         "unitCellAngleBeta.pkl",
         "unitCellAngleGamma.pkl",
         "vitrification.pkl"]

    overview = []
    init_db = pd.read_pickle("Database/External/{0}".format("chainLength.pkl"))
    full_table = init_db.drop(columns='chainLength', axis=1)
    merge_process = {}
    for f in useable:
        cur_db = pd.read_pickle("Database/External/{0}".format(f))
        overview.append(
            pd.DataFrame(
                {"file_name": f,
                 "name": re.sub('.pkl', '', f),
                 "nrow": cur_db.shape[0],
                 "col_names": [", ".join(map(str, list(cur_db.columns[1::])))]
                 }
            )
        )
        if 'chainId' in list(cur_db.columns):
            full_table = full_table.merge(cur_db, on=['pdb_code', 'chainId'])
        else:
            full_table = full_table.merge(cur_db, on=['pdb_code'])
            nrow = full_table.shape[0]
        merge_process[f] = {"new_col": f, 'nrow': nrow}

    overview = pd.concat(overview)
    overview.reset_index(inplace=True, drop=True)

    # def create_frontend_names(overview):
    #     overview["frontend_names"] = None
    #     for row in range(overview.shape[0]):
    #         overview["frontend_names"][row] = overview.col_names[row] \
    #             + " (" + overview.data_type[row] + ")"
    #     return overview
    # overview = create_frontend_names(overview)
    return [full_table, overview, merge_process]


res = subset_useable_data()
pd.to_pickle('Database/full_prototypeDB.pkl', obj=res[0])
