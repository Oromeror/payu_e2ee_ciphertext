--
-- Data base: endtoendencryption
--

DROP DATABASE IF EXISTS endtoendencryption;
CREATE DATABASE IF NOT EXISTS endtoendencryption;
USE endtoendencryption;

-- --------------------------------------------------------

--
-- Table structure for transaction entity
--

CREATE TABLE IF NOT EXISTS card_e2ee (
    ciphertext varchar(255)
);