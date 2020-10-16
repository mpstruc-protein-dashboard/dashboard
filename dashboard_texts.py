class dashboard_texts():

    #     no_of_entries = ..
    #     db_types_len = ..
    #     db_types_as_str = ..
    #     features_as_str = ..

    def mpstruc_description_text():
        mpstruc_text = """
                mpstruc is a curated database of membrane proteins of known 3D structure from the Stephen White laboratory at UC Irvine.
                To be included in the database, a structure must be available in the RSCB Protein Data Bank (PDB) and have been published in a peer reviewed journal.
                The database is manually curated based upon on-going literature surveys.
                Because of the labor involved, new structures are not posted until they are released by the PDB and the complete reference,
                including pagination for print journals, is available in PubMed.
                Their goal is to make mpstruc as accurate and complete as possible.
                If you find errors or omissions, please send a message to Stephen White, Gracie Han (gyewon.han@usc.edu),
                or Craig Snider. mpstruc emphasizes structures determined by diffraction and cryo-EM methods.
                NMR structures are also included whenever identified. A comprehensive list of NMR-determined
                structures has been established by Dror Warschawski and is available from the Antoine Loquet lab. 
                (source: https://blanco.biomol.uci.edu/mpstruc/)
                """
        return mpstruc_text

    def dashboard_description_text():
        dash_text = """ 
                This dashboard shall enable its user to visually explore the mpstruc database and its contents
                by providing a base-line report aswell as a do-it-yourself sandbox visualization system, that
                allowes the expierienced user to customize the vizualitaions to their liking.
                """
        return dash_text

    def timeline_text(no_of_entries, db_types_len, db_types_as_str, features_as_str, lastDatabaseEditDate_str):
        text_timeline = """
                The database up-to-date holds {0} records which are divided into {1} categories: {2}. Features reported include {3}.\n\n
                It was last updated at: {4}.
                """.format(no_of_entries, db_types_len, db_types_as_str, features_as_str, lastDatabaseEditDate_str)
        return text_timeline

    def plot_timeline_text(no_of_entries,
                           no_of_monotopic_proteins,
                           mono_prot_ratio,
                           no_of_alpha_proteins,
                           alpha_prot_ratio,
                           no_of_beta_proteins,
                           beta_prot_ratio):
        text_plot_timeline = """
                The following figure depicts the increasing pace in which entries are added to the mpstruc database.
                It shows the start of an somewhat exponantional growth. The more data there is the harder it gets to
                keep an rigid overview about the database's contents. This dashboard shall provide such basic overview to keep track of the
                database and its progression. One thing to notice right away is the ratio between the entries. Out of {0} entries {1} are monotopic proteins ({2}%),
                the majority of {3} are alpha helical ({4}%) and {5} are beta barrel proteins ({6}%).""".format(no_of_entries,
                                                                                                                no_of_monotopic_proteins,
                                                                                                                mono_prot_ratio,
                                                                                                                no_of_alpha_proteins,
                                                                                                                alpha_prot_ratio,
                                                                                                                no_of_beta_proteins,
                                                                                                                beta_prot_ratio)
        return text_plot_timeline

    def text_resolution_over_time(alpha_prot_ratio):
        text_resolution_over_time = """
                Over time also the resolution at which proteins are identified and validated changes.
                This is depicted as the change in mean resolution over time for all database types in the next figure.
                The slope has a slight positive trend so it seems the resolution of membrane proteins improves over time. 
                This view is heavily skewed by the ratio of entries. In other words approximately {0}% of the trend is due to the alpha helical structures
                and their high occurance in the database.
                """.format(alpha_prot_ratio)
        return text_resolution_over_time

# def mono
#     mono_text = '''
#     Out of {0} database entries there are {1} monotopic membrane proteins, so {2}%. \n
#     Their mean resolution is:
#     '''.format(no_of_entries, no_of_monotopic_proteins, round(mono_prot_ratio, 2))
