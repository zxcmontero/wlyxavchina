def test_about_content(client):
    rv = client.get('/about')
    assert rv.status_code == 200
    text = rv.get_data(as_text=True)
    assert 'Подбираем специалистов для офисных и операционных команд' in text
    assert 'Короткий бриф' in text or 'Шаг 1' in text


def test_contacts_address(client):
    rv = client.get('/contacts')
    assert rv.status_code == 200
    assert 'ул. Деловая' in rv.get_data(as_text=True)


def test_footer_present(client):
    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_data(as_text=True)
    assert 'Поиск работы и подбор персонала' in data
    assert '<footer class="site-footer"' in data
