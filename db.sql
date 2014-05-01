CREATE TABLE `queries` (
	`name` varchar(255) NOT NULL,
	`type` varchar(10) NOT NULL DEFAULT 'A',
	`src` int(10) unsigned NOT NULL DEFAULT '0',
	`dst` int(10) unsigned NOT NULL DEFAULT '0',
	`last_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`hits` int(10) unsigned NOT NULL DEFAULT '0',
	PRIMARY KEY (`name`,`type`,`src`,`dst`),
	KEY `last_time` (`last_time`),
	KEY `hits` (`hits`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
