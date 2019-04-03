# coding=utf-8

import psycopg2
import pandas as pd
import saninco_docs.jdbc_conf as jdbc
from sshtunnel import SSHTunnelForwarder


_SQL_QUERY_TRAINING = "SELECT " \
                      "rs.\"id\" AS \"realtorSearchId\", " \
                      "rs.province, " \
                      "rs.city, " \
                      "rs.address, " \
                      "rs.\"postalCode\", " \
                      "TRIM (rs.longitude) :: NUMERIC AS longitude, " \
                      "TRIM (rs.latitude) :: NUMERIC AS latitude, " \
                      "rs.price, " \
                      "rs.\"buildingTypeId\", " \
                      "rs.\"tradeTypeId\", " \
                      "to_char(rs.\"listingDate\", 'YYYY-MM-DD') AS \"listingDate\", " \
                      "date_part( 'day', rs.\"delislingDate\" :: TIMESTAMP - rs.\"listingDate\" :: TIMESTAMP ) " \
                      "AS \"daysOnMarket\", " \
                      "( rh.\"realtorData\" -> 'Building' ->> 'Bedrooms' ) AS bedrooms, " \
                      "( rh.\"realtorData\" -> 'Building' ->> 'BathroomTotal' ) AS \"bathroomTotal\", " \
                      "( rh.\"realtorData\" -> 'Property' ->> 'Type' ) AS \"propertyType\", " \
                      "( rh.\"realtorData\" -> 'Property' ->> 'OwnershipType' ) AS \"ownerShipType\" " \
                      "FROM realtor_search rs " \
                      "INNER JOIN realtor_history rh ON rs.\"pMlsNumber\" = rh.\"pMlsNumber\" " \
                      "WHERE " \
                      "rs.\"delislingDate\" IS NOT NULL " \
                      "AND rs.latitude IS NOT NULL " \
                      "AND rs.longitude IS NOT NULL " \
                      "AND rs.latitude != '' " \
                      "AND rs.longitude != '' "


def get_training_data(limit=None, sql=_SQL_QUERY_TRAINING):
    if limit is not None:
        sql = sql + (" LIMIT %s " % limit)

    _data = execute_query(query_fn=lambda conn, _sql=sql: pd.read_sql_query(sql=_sql, con=conn))

    return _data


_SQL_QUERY_PREDICT = "SELECT DISTINCT " \
                     "rp.\"id\" AS \"realtorDataPredictId\", " \
                     "rp.\"realtorDataId\", " \
                     "rd.province, " \
                     "LOWER (COALESCE (NULLIF (TRIM(city), ''), 'none')) AS city, " \
                     "rd.address, " \
                     "COALESCE (" \
                     "NULLIF ( " \
                     "LOWER (SUBSTRING (regexp_replace(TRIM (rd.\"postalCode\"), '[?,-.&;]', '', 'g') FROM 1 FOR 3))" \
                     ", '')" \
                     ", 'none') AS \"postalCode\", " \
                     "COALESCE ( NULLIF ( LOWER (TRIM(rd.district)), '' ), 'none' ) AS district, " \
                     "TRIM (rd.longitude) :: NUMERIC AS longitude, " \
                     "TRIM (rd.latitude) :: NUMERIC AS latitude, " \
                     "rd.price, " \
                     "rd.\"buildingTypeId\", " \
                     "rd.\"tradeTypeId\", " \
                     "to_char( rd.\"listingDate\", 'YYYY-MM-DD' ) AS \"listingDate\", " \
                     "( rh.\"realtorData\" -> 'Building' ->> 'Bedrooms' ) AS bedrooms, " \
                     "( rh.\"realtorData\" -> 'Building' ->> 'BathroomTotal' ) AS \"bathroomTotal\", " \
                     "( rh.\"realtorData\" -> 'Property' ->> 'Type' ) AS \"propertyType\", " \
                     "NULLIF (LOWER ( rh.\"realtorData\" -> 'Property' ->> 'OwnershipType' ), 'none') " \
                     "AS \"ownerShipType\" " \
                     "FROM realtor_data_predict rp " \
                     "INNER JOIN realtor_data rd ON rp.\"realtorDataId\" = rd.\"id\" " \
                     "INNER JOIN realtor_history rh ON rd.\"pMlsNumber\" = rh.\"pMlsNumber\" " \
                     "WHERE rp.\"domByAI\" IS NULL " \
                     "AND rd.latitude IS NOT NULL " \
                     "AND rd.longitude IS NOT NULL " \
                     "AND rd.latitude != '' " \
                     "AND rd.longitude != ''"


def get_predict_data(limit=None, sql=_SQL_QUERY_PREDICT):
    if limit is not None:
        sql = sql + (" LIMIT %s " % limit)

    _data = execute_query(query_fn=lambda conn, _sql=sql: pd.read_sql_query(sql=_sql, con=conn))

    return _data


def get_city_dictionary():
    sql = "SELECT DISTINCT " \
          "LOWER ( " \
          "COALESCE (NULLIF (TRIM(city), ''), 'none') "\
          ") AS dictionary "\
          "FROM "\
          "realtor_data "\
          "ORDER BY dictionary"
    _data = execute_query(sql=sql)
    result = []
    for row in _data:
        result.append(row[0])

    return result


def get_province_dictionary():
    sql = 'SELECT "name" FROM province ORDER BY province'
    _data = execute_query(sql=sql)
    result = []
    for row in _data:
        result.append(row[0])

    return result


def get_postcode_dictionary():
    sql = "SELECT DISTINCT " \
          "COALESCE (" \
          "NULLIF ( " \
          "LOWER (SUBSTRING (regexp_replace(TRIM (rd.\"postalCode\"), '[?,-.&;]', '', 'g') FROM 1 FOR 3))" \
          ", '')" \
          ", 'none')" \
          " AS \"postalCode\" " \
          "FROM realtor_data rd " \
          "ORDER  BY  \"postalCode\" "
    _data = execute_query(sql=sql)
    result = []
    for row in _data:
        result.append(row[0])

    return result


def get_ownership_dictionary():
    sql = "SELECT DISTINCT " \
          "NULLIF (LOWER ( rh.\"realtorData\" -> 'Property' ->> 'OwnershipType' ), 'none') AS \"ownerShipType\" " \
          "FROM realtor_data rd INNER JOIN realtor_history rh ON rd.\"pMlsNumber\" = rh.\"pMlsNumber\"  " \
          "ORDER BY \"ownerShipType\""
    _data = execute_query(sql=sql)
    result = []
    for row in _data:
        result.append(row[0])

    return result


def get_district_dictionary():
    sql = "SELECT DISTINCT COALESCE ( NULLIF ( LOWER (TRIM(rd.district)), '' ), 'none' ) AS district " \
          "FROM realtor_data rd ORDER BY district"
    _data = execute_query(sql=sql)
    result = []
    for row in _data:
        result.append(row[0])

    return result


def do_predict_fn():

    sql = "SELECT fn_predict_dom_main()"
    execute_query(sql=sql, is_select=False)


def do_predict_finish():

    sql = "SELECT fn_predict_dom_finish()"
    _data = execute_query(sql=sql)
    for row in _data:
        _data = row[0]
    return _data


def update_predict_data(_data):

    def _batch_update(con, data):
        cursor = con.cursor()
        for index, row in data.iterrows():
            sql = 'UPDATE realtor_data_predict SET "domByAI" = %s ' \
                  'WHERE "id" = %s ' % (int(row["predict"]), int(row["realtorDataPredictId"]))
            cursor.execute(sql)
        con.commit()
        con.close()

    execute_query(query_fn=lambda conn, data=_data: _batch_update(con=conn, data=data))


def insert_predict_data(_data):
    """
    Notes
        data: data must be include "realtorSearchId","realtorDataId","predictDaysOnMarket"
    """
    _insert_query = "INSERT INTO realtor_search_ai_predict( " \
                    "\"realtorSearchId\", " \
                    "\"realtorDataId\", " \
                    "\"predictDaysOnMarket\", " \
                    "\"createdTimestamp\" ) " \
                    "VALUES "
    i = 0
    for index, row in _data.iterrows():
        if i > 0:
            _insert_query += ','
        _insert_query += '(%s, %s, %s, now())' % (int(row["realtorSearchId"]),
                                                      int(row["realtorDataId"]),
                                                      int(row["predict"]))
        i += 1
    execute_query(sql=_insert_query, is_select=False)


def execute_query(sql=None, query_fn=None, is_select=True):
    def _query(conn, _sql=sql, _query_fn=query_fn):
        __data = None
        if query_fn is not None:
            __data = query_fn(conn)
        elif sql is not None:
            try:
                if is_select:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    __data = cursor.fetchall()
                    cursor.close()
                    conn.commit()
                else:
                    cursor = conn.cursor()
                    cursor.execute(sql)
                    __data = cursor.rowcount
                    conn.commit()

            except ZeroDivisionError as e:
                print(e)
            finally:
                conn.close()

        return __data

    return _do_query(query_fn=lambda conn: _query(conn))


def _do_query(query_fn, is_ssh=jdbc.is_ssh):
    if is_ssh:
        with SSHTunnelForwarder((jdbc.ssh_host, jdbc.ssh_port),
                                ssh_password=jdbc.ssh_password, ssh_username=jdbc.ssh_username,
                                remote_bind_address=(jdbc.host, jdbc.port)) as server:

            conn = psycopg2.connect(
                host='localhost',
                port=server.local_bind_port,
                database=jdbc.database,
                user=jdbc.user,
                password=jdbc.password
            )
            return query_fn(conn)
    else:
        conn = psycopg2.connect(
            host=jdbc.host,
            port=jdbc.port,
            database=jdbc.database,
            user=jdbc.user,
            password=jdbc.password
        )
        return query_fn(conn)


if __name__ == "__main__":
    # province_dictionary = get_province_dictionary()
    # city_dictionary = get_city_dictionary()
    ownership_dictionary = list(filter(None, get_ownership_dictionary()))
    print(ownership_dictionary)
    # dictionaries = {"city_dictionary": city_dictionary, "province_dictionary": province_dictionary}
    # # dictionaries = [{"city_dictionary": city_dictionary}]
    # with open(conf.model_dictionary_path, 'w+', encoding='utf-8') as f:
    #     f.writelines(str(dictionaries))
    #     f.close()
    # postcode_dictionary = get_postcode_dictionary()
    # postcode_first_three_list = []
    # for _item in postcode_dictionary:
    #     print(_item)
    #     if _item not in postcode_first_three_list:
    #         postcode_first_three_list.append(_item.split(' ')[0])
    # print(postcode_first_three_list)
    # data = get_training_data(limit=10)
    # print(data)

#
#     data = get_predict_data(limit=10)
#     print(data)
