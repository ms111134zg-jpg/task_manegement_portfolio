BEGIN;

-- 検証用user seed作成
INSERT INTO users (id, name, email)
VALUES
(1, 'TestA', 'testa@example.com'),
(2, 'TestB', 'testb@example.com'),
(3, 'TestC', 'testc@example.com')
ON CONFLICT (id) DO NOTHING
;


SELECT setval(pg_get_serial_sequence('users','id'),
              (SELECT COALESCE(MAX(id),0) FROM users), true);


-- 検証用tasks seed作成
INSERT INTO tasks
(id, user_id, title, description, status, priority, due_date)
VALUES
(1, 1, 'Add pagination', 'list APIにlimit/offset/totalを追加', 'todo', 2, '2026-02-20'),
(2, 1, 'Implement filters', 'status/user/dateのファイル追加', 'doing', 3, '2026-02-18'),
(3, 1, 'Write README', '起動手順・API例・ER図を記載', 'todo', 4, '2026-02-25'),
(4, 1, 'Fix updated_at', '更新時にupdated_atが変わるようにする', 'done', 3, NULL),
(5, 1, 'Add stats endpoint', 'status別件数の集計API追加', 'todo', 5, '2026-02-24'),
(6, 2, 'Prepare DB schema', 'users/tasksのDDLを整備', 'done', 2, NULL),
(7, 2, 'Users API', 'usersの作成・一覧・詳細を実装', 'doing', 3, '2026-02-16'),
(8, 2, 'Tasks API', 'tasks CRUDの実装', 'todo', 3, '2026-02-19'),
(9, 2, 'Add validations', 'status/priority/titleのバリデーション', 'todo', 4, NULL),
(10, 2, 'Refactor routes', 'routers分割、責務整理', 'todo', 5, NULL),
(11, 3, 'Sample overdue task', 'due_toフィルタ確認用（期限切れ）', 'todo', 1, '2026-02-01'),
(12, 3, 'Task search test', 'q=での部分一致検索確認', 'doing', 2, '2026-02-17'),
(13, 3, 'Sort test', 'priorityソートの確認', 'todo', 4, NULL),
(14, 3, 'Delete task test', 'DELETE動作確認用', 'done', 3, NULL),
(15, 3, 'Edge case: empty desc', 'descriptionがNULLでも問題ないか確認', 'todo', 3, '2026-02-22')
ON CONFLICT (id) DO NOTHING
;

SELECT setval(pg_get_serial_sequence('tasks','id'),
              (SELECT COALESCE(MAX(id),0) FROM tasks), true);



COMMIT;