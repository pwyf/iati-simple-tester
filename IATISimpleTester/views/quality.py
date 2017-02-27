from flask import render_template, jsonify, request

from IATISimpleTester import app, db, helpers
from IATISimpleTester.models import SuppliedData


@app.route('/quality/<uuid:uuid>')
def package_quality(uuid):
    data = SuppliedData.query.get(str(uuid))
    all_activities = helpers.load_activities_from_package(data.path_to_file())

    tests = request.args.get('tests')
    filter_ = request.args.get('filter')

    if tests in app.config['TEST_SETS']:
        test_set = app.config['TEST_SETS'].get(tests)
    else:
        test_set = app.config['TEST_SETS']['pwyf']

    # load the tests
    all_tests_list, all_filters_list = helpers.load_expressions_from_yaml(test_set['tests_file'])

    # set the filter
    current_filter = all_filters_list[0] if filter_ else None

    # single_test = helpers.select_expression(all_tests_list, request.args.get('test'))

    # page = int(request.args.get('page', 1))
    # offset = (page - 1) * app.config['PER_PAGE']

    activities = helpers.filter_activities(all_activities, current_filter)
    activities_results, results_summary = helpers.test_activities(activities, all_tests_list)

    # pagination = Pagination(page, app.config['PER_PAGE'], num_activities)

    # activities_results[id_] = activities_results[offset:offset + app.config['PER_PAGE']]

    return jsonify({'success': True, 'data': {'results': activities_results, 'summary': results_summary}})
