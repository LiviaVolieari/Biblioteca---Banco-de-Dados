CREATE DATABASE IF NOT EXISTS biblioteca;
USE biblioteca;


CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    senha VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS autores (
    id_autor INT AUTO_INCREMENT PRIMARY KEY,
    nome_autor VARCHAR(255) NOT NULL,
    nacionalidade VARCHAR(255),
    data_nascimento DATE,
    biografia TEXT
);


CREATE TABLE IF NOT EXISTS generos (
    id_genero INT AUTO_INCREMENT PRIMARY KEY,
    nome_genero VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS editoras (
    id_editora INT AUTO_INCREMENT PRIMARY KEY,
    nome_editora VARCHAR(255) NOT NULL,
    endereco_editora TEXT
);


CREATE TABLE IF NOT EXISTS livros (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    ano INT,
    isbn VARCHAR(20),
    quantidade INT DEFAULT 1,
    resumo TEXT,
    autor_id INT,
    genero_id INT,
    editora_id INT,
    FOREIGN KEY (autor_id) REFERENCES autores(id_autor),
    FOREIGN KEY (genero_id) REFERENCES generos(id_genero),
    FOREIGN KEY (editora_id) REFERENCES editoras(id_editora)
);


CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    livro_id INT,
    data_emprestimo DATE,
    data_devolucao_prevista DATE,
    data_devolucao_real DATE,
    status_emprestimo ENUM('pendente', 'devolvido', 'atrasado'),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (livro_id) REFERENCES livros(id)
);

CREATE TABLE auditoria_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabela_afetada VARCHAR(50),
    operacao ENUM('INSERT', 'UPDATE', 'DELETE'),
    usuario_responsavel INT,
    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    dados_anteriores TEXT,
    dados_novos TEXT
);


-- ADIÇÃO NA TABELA USUÁRIOS PARA AJUDAR OS TRIGGER
ALTER TABLE usuarios
ADD status ENUM('ativo', 'inativo') DEFAULT 'ativo';


-- CRIAÇÃO DE FUNÇÕES DE APOIO
-- primeira função – Verificar se o usuário tem empréstimos atrasados

DELIMITER //
CREATE FUNCTION usuario_tem_atraso(p_usuario_id INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE qtd INT;
    SELECT COUNT(*) INTO qtd
    FROM emprestimos
    WHERE usuario_id = p_usuario_id
      AND status_emprestimo = 'atrasado';

    RETURN qtd > 0;
END//
DELIMITER ;


-- segunda função – Verificar disponibilidade do livro
DELIMITER //
CREATE FUNCTION livro_disponivel(p_livro_id INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE qtd INT;
    SELECT quantidade INTO qtd
    FROM livros
    WHERE id = p_livro_id;
    RETURN qtd > 0;
END//
DELIMITER ;

-- CRIAÇÃO DE PROCEDIMENTO DE APOIO
DELIMITER //
CREATE PROCEDURE validar_datas(
    IN p_data_emp DATE,
    IN p_data_prev DATE
)
BEGIN
    IF p_data_prev <= p_data_emp THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Data de devolução deve ser posterior à data de empréstimo';
    END IF;
END//
DELIMITER ;

-- Capturar Usuário Atual
DELIMITER //
CREATE FUNCTION usuario_atual()
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN 1; -- usuário logado (simulado)
END//
DELIMITER ;


-- ** GATILHOS **

-- Bloquear empréstimo se o usuário estiver INATIVO

DELIMITER //
CREATE TRIGGER validar_atividadeusuario
BEFORE INSERT ON emprestimos
FOR EACH ROW
BEGIN
    DECLARE situacao ENUM('ativo', 'inativo');
    SELECT status INTO situacao
    FROM usuarios
    WHERE id = NEW.usuario_id;
    IF situacao = 'inativo' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Usuário inativo não pode realizar empréstimos';
    END IF;
END//
DELIMITER ;

-- Impedir empréstimo se o usuário tiver com um livro em atraso

DELIMITER //
CREATE TRIGGER bloquear_usuarioatraso
BEFORE INSERT ON emprestimos
FOR EACH ROW
BEGIN
    IF usuario_tem_atraso(NEW.usuario_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Usuário possui empréstimos em atraso';
    END IF;
END//
DELIMITER ;


-- Impedir empréstimo se o livro estiver indisponível
DELIMITER //
CREATE TRIGGER validar_disponibilidade_livro
BEFORE INSERT ON emprestimos
FOR EACH ROW
BEGIN
    IF NOT livro_disponivel(NEW.livro_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Livro indisponível para empréstimo';
    END IF;
END//
DELIMITER ;

-- Validar datas do empréstimo
DELIMITER //
CREATE TRIGGER validar_datas_emprestimo
BEFORE INSERT ON emprestimos
FOR EACH ROW
BEGIN
    CALL validar_datas(
        NEW.data_emprestimo,
        NEW.data_devolucao_prevista
    );
END//
DELIMITER ;

-- Impedir cadastro de ISBN duplicado
DELIMITER //
CREATE TRIGGER bloquear_isbn_duplicado
BEFORE INSERT ON livros
FOR EACH ROW
BEGIN
    DECLARE qtd INT;
    SELECT COUNT(*) INTO qtd
    FROM livros
    WHERE isbn = NEW.isbn;
    IF qtd > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'ISBN já cadastrado no sistema';
    END IF;
END//
DELIMITER ;


-- Auditoria de INSERT em usuários

DELIMITER //
CREATE TRIGGER auditoria_insert_usuario
AFTER INSERT ON usuarios
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_logs (
        tabela_afetada, operacao, usuario_responsavel, dados_novos
    )
    VALUES (
        'usuarios',
        'INSERT',
        usuario_atual(),
        CONCAT('Nome: ', NEW.nome, ' Email: ', NEW.email)
    );
END//
DELIMITER ;

-- Auditoria de UPDATE em usuários

-- **** não fucionar, vou ajeitar dps****
DELIMITER //
CREATE TRIGGER tg_auditoria_update_usuario
AFTER UPDATE ON usuarios
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO auditoria_logs (
             tabela_afetada,
             operacao,
             usuario_responsavel,
             dados_anteriores,
             dados_novos
         ) VALUES (
             'usuarios',
             'UPDATE',
             NULL,
             CONCAT('Status anterior: ', IFNULL(OLD.status, 'NULO')),
             CONCAT('Status novo: ', IFNULL(NEW.status, 'NULO'))
         );
     END IF;
 END;
 //
DELIMITER ;

-- Auditoria de INSERT em empréstimos
DELIMITER //
CREATE TRIGGER auditoria_insert_emprestimo
AFTER INSERT ON emprestimos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_logs (
        tabela_afetada, operacao, usuario_responsavel, dados_novos
    )
    VALUES (
        'emprestimos',
        'INSERT',
        usuario_atual(),
        CONCAT(
            'Usuário: ', NEW.usuario_id,
            ' Livro: ', NEW.livro_id,
            ' Data empréstimo: ', NEW.data_emprestimo
        )
    );
END//
DELIMITER ;

-- Auditoria de UPDATE em empréstimos
DELIMITER //
CREATE TRIGGER auditoria_update_emprestimo
AFTER UPDATE ON emprestimos
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_logs (
        tabela_afetada, operacao, usuario_responsavel,
        dados_anteriores, dados_novos
    )
    VALUES (
        'emprestimos',
        'UPDATE',
        usuario_atual(),
        CONCAT('Status anterior: ', OLD.status_emprestimo),
        CONCAT('Status novo: ', NEW.status_emprestimo)
    );
END//
DELIMITER ;

-- Auditoria de DELETE em livros 

-- **** não fucionar, vou ajeitar dps****
DELIMITER //
CREATE TRIGGER auditoria_delete_livro
AFTER DELETE ON livros
FOR EACH ROW
BEGIN
    INSERT INTO auditoria_logs (
        tabela_afetada, operacao, usuario_responsavel, dados_anteriores
    )
    VALUES (
        'livros',
        'DELETE',
        usuario_atual(),
        CONCAT(
            'Livro removido: ', OLD.titulo,
            ' ISBN: ', OLD.isbn
        )
    );
END//
DELIMITER ;


