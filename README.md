# Under Contruction

Proof of Concept

1. Start PSQL
2. `bash database_management_scripts/setup_psql.sh`
3. `python fingerprint_directory_of_files.py test_wav`
4. `python match_song test_wav/samples_for_test/Bust_This_subsection.wav`

Output:
> Bust_This_Bust_That.wav


Match Counts (not shown currently):
>(DEBUG ONLY) {'I_Want_To_Destroy_Something_Beautiful.wav': 11, 
'Bust_This_Bust_That.wav': 53, 'jazz_club.wav': 6, 
'Sonic_Marble_Zone.wav': 4, 'SMB_Overworld.wav': 4})