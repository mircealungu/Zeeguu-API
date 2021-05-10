from zeeguu_core.sql.query_building import date_format
import zeeguu_core
from statistics import mean

db = zeeguu_core.db


def summarize_reading_activity(user_id, cohort_id, start_date, end_date):
    def _mean(l):
        if len(l) == 0:
            return 0
        return int(mean(l))

    r_sessions = reading_sessions(user_id, cohort_id, start_date, end_date)

    distinct_texts = set()
    reading_time = 0
    text_lengths = []
    text_difficulties = []
    for session in r_sessions:
        if session["title"] not in distinct_texts:
            text_lengths.append(session["word_count"])
            text_difficulties.append(session["difficulty"])
            distinct_texts.add(session["title"])

        reading_time += session["duration_in_sec"]

    number_of_texts = len(distinct_texts)

    return {
        "number_of_texts": number_of_texts,
        "reading_time": reading_time,
        "average_text_length": _mean(text_lengths),
        "average_text_difficulty": _mean(text_difficulties),
    }


"""
    Example where clause:
            
            user_id = 534
            and start_time > '2021-04-01'
            and last_action_time < '2021-05-01'
            and duration > 0
            and language_id = (select language_id from `cohort` where cohort.id=6)
        
          
"""


def reading_sessions(user_id, cohort_id, start_date, end_date):

    query = """
            select  u.id as session_id, 
                user_id, 
                start_time, 
                last_action_time as end_time,
                truncate((duration / 1000),0) as duration_in_sec,
                article_id, 
                a.title,
                a.word_count,
                a.fk_difficulty as difficulty,
                a.language_id
        
        
        from user_reading_session as u
        
        join article as a
            on u.article_id = a.id
            
        where 
            user_id = :userId
            and start_time > :startDate
            and last_action_time < :endDate
            and duration > 0
            and language_id = (select language_id from `cohort` where cohort.id=:cohortId)
        
        
        order by start_time desc
    """

    rows = db.session.execute(
        query,
        {
            "userId": user_id,
            "startDate": date_format(start_date),
            "endDate": date_format(end_date),
            "cohortId": cohort_id,
        },
    )

    result = []
    for row in rows:
        session = dict(row)
        session["translations"] = translations_in_interval(
            session["start_time"], session["end_time"]
        )
        result.append(session)

    return result


"""
    Example where clause: 

        b.time > '2021-04-17 15:20:09'
        and b.time < '2021-04-17 15:22:43'
    
"""


def translations_in_interval(start_time, end_time):

    query = """
        select 
            b.id, 
            uw.word, 
            uwt.word as translation,
            IF(bem.bookmark_id IS NULL, FALSE, TRUE) as practiced
        
        from bookmark as b	
        
        join user_word as uw
           on b.origin_id = uw.id
           
        join user_word as uwt
           on b.translation_id = uwt.id
        
        left join bookmark_exercise_mapping as bem
           on bem.bookmark_id = b.id

        where 
            b.time > :start_time
            and b.time < :end_time

    """

    rows = db.session.execute(
        query,
        {"start_time": start_time, "end_time": end_time},
    )

    result = []
    for row in rows:
        session = dict(row)
        result.append(session)

    return result
