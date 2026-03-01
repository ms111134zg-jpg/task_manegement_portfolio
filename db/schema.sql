-- users, tasksのテーブル定義・作成

CREATE TABLE users (
    id         BIGSERIAL    PRIMARY KEY,
    name       VARCHAR(80)  NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    title VARCHAR(120) NOT NULL,
    description TEXT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'todo',
    priority SMALLINT NOT NULL DEFAULT 3,
    due_date DATE NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tasks_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id)  ON DELETE RESTRICT,
    CHECK (status IN ('todo', 'doing', 'done')),
    CHECK (priority BETWEEN 1 AND 5)
);


-- tasksのindex作成
CREATE INDEX idx_id ON tasks (id);
CREATE INDEX idx_status ON tasks (status);
CREATE INDEX idx_due ON tasks (due_date);
CREATE INDEX idx_update ON tasks (updated_at);