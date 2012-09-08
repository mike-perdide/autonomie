INSERT into accounts  (`login`, `password`, `firstname` ,`lastname`, `email`, `active`) VALUES ('user1_login', '24c9e15e52afc47c225b757e7bee1f9d', 'user1_firstname', 'user1_lastname', 'user1@test.fr', 'Y');
INSERT into company (`name`, `object`, `phone`, `creationDate`, `updateDate`, `logo`, `header`) VALUES ('company1', 'Company of user1', '0457858585', '1286804741', '1286804741', 'logo.png', 'header.png');
INSERT into company_employee (`company_id`, `account_id`) VALUES ('1', '1');
INSERT into customer (`id`, `code`, `name`, `creationDate`, `updateDate`, `company_id`) VALUES ('1', 'C001', 'Client1', '1286804741', '1286804741', '1');
INSERT into project (`id`, `name`, `client_id`, `code`, `definition`, `creationDate`, `updateDate`, `company_id`) VALUES ('1', 'Projet de test', '1', 'P001', 'Projet de test', '1286804741', '1286804741', '1');
INSERT into phase (`id`, `name`, `project_id`, `creationDate`, `updateDate`) VALUES ('1', 'Phase de test', '1', '1286804741', '1286804741');

INSERT INTO `config` VALUES ('phpgwapi','site_title','Test Autonomie'), ('phpgwapi','hostname','autonomie.localhost'), ('coopagest','coop_estimationfooter','Après signature du client, ce devis prendra valeur de bon de commande dès son retour par courrier ou validation par mail en précisant le N° de devis et le montant.\r\n\r\nCachet de l\'entreprise, Nom, fonction et signature du client précédée de la mention « bon pour accord ».\r\n\r\n'),('coopagest','coop_pdffootertitle','Centre de facturation PORT PARALLELE SCOP/SARL à  capital variable'),('coopagest','coop_pdffootercourse','Organisme de formation N° de déclaration d\'activité au titre de la FPC : 11 75 4210875'),('coopagest','coop_pdffootertext','RCS PARIS 492 196 209 - SIRET 492 196 209 000 26 - Code naf 7022Z TVA INTRACOM : FR28492196209\r\nSiège social : 70, rue Amelot 75011 Paris - tel: 00 (33) 1 53 19 96 15'),('coopagest','coop_administratorgroup','-10'),('coopagest','coop_employeesgroup','-135'),('coopagest','coop_interviewergroup','315'),('coopagest','coop_specialuser','134'),('coopagest','coop_estimationaddress','Port Parallèle\r\n70, rue Amelot \r\n75011 Paris'),('coopagest','coop_invoicepayment','Par chèque libellé à l\'ordre de : Port Parallèle Production/ %ENTREPRENEUR% \r\nOu par virement sur le compte de Port Parallèle Production/ %ENTREPRENEUR%\r\nCrédit coopératif Paris gare de l\'Est \r\nRIB : %RIB%\r\nIBAN : %IBAN%\r\nBIC : CCOPFRPPXXX'),('wiki','allow_anonymous','True'),('coopagest','coop_invoicelate','Tout retard de paiement entraînera à titre de clause pénale, conformément à la loi 92.1442 du 31 décembre 1992, une pénalité égale à un taux d\'intérêt équivalent à  une fois et demi le taux d\'intérêt légal en vigueur à cette échéance.'), ('phpgwapi','files_dir','/var/intranet_files/files');
