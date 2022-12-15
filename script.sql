
##### groupes

CREATE TABLE `groupes` (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) CHARACTER SET utf8mb3 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE `groupes`
  ADD UNIQUE KEY `nom` (`nom`);

INSERT INTO `groupes` (`nom`) VALUES
  ("gojira");

##### concerts

CREATE TABLE `concerts` (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `nom` varchar(255) CHARACTER SET utf8mb3 NOT NULL,
  `date` varchar(255) CHARACTER SET utf8mb3 NOT NULL,
  `groupe_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `concerts` (`nom`, `date`, `groupe_id`) VALUES
  ("GozillaTour", "15/12/2022", 1);

ALTER TABLE `concerts`
  ADD UNIQUE KEY `nom` (`nom`);
ALTER TABLE `concerts`
  ADD KEY (`groupe_id`);

##### tickets

CREATE TABLE `tickets` (
  `id` int(11) PRIMARY KEY NOT NULL AUTO_INCREMENT,
  `place` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `available` TINYINT NOT NULL,
  `concert_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `tickets` (`place`,`price`, `available`, `concert_id`) VALUES 
  (33, 500, 1, 2);

ALTER TABLE `tickets`
  ADD KEY (`concert_id`);

#### ajout constraints

ALTER TABLE `tickets`
  ADD CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`concert_id`) REFERENCES `concerts` (`id`);

ALTER TABLE `concerts`
  ADD CONSTRAINT `concerts_ibfk_1` FOREIGN KEY (`groupe_id`) REFERENCES `groupes` (`id`);
